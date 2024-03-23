import os
from typing import Annotated

from fastapi import FastAPI, UploadFile, Form
from starlette.background import BackgroundTask
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from dspace import generate_dublin_core_xml, build_saf_file
from dto import ThesisMetadata
from inference import extract_metadata, extract_keywords
from pdf_utils import edit_pdf, extract_cover_page_and_abstract

app_ui = FastAPI()
app_api = FastAPI()

static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
print("static_path:", static_path)

app_ui.mount("/api/v1", app_api)
app_ui.mount("/", StaticFiles(directory=static_path, html=True), name="static")


@app_api.post("/inferMetadata")
def infer_metadata(document: UploadFile) -> ThesisMetadata:
    cover_page, abstract = extract_cover_page_and_abstract(document.file)

    cover_page_metadata = extract_metadata(cover_page)
    keywords = extract_keywords(abstract)

    return ThesisMetadata(
        advisors=cover_page_metadata.advisors,
        authors=cover_page_metadata.authors,
        code="",
        issued=cover_page_metadata.issued,
        abstract=abstract,
        language="",
        subjects=keywords,
        title=cover_page_metadata.title,
        document_type=""
    )


@app_api.post("/getSafFile")
def get_saf_file(
        document: UploadFile,
        advisors: Annotated[list[str], Form()],
        authors: Annotated[list[str], Form()],
        code: Annotated[str, Form()],
        issued: Annotated[str, Form()],
        abstract: Annotated[str, Form()],
        language: Annotated[str, Form()],
        subjects: Annotated[list[str], Form()],
        title: Annotated[str, Form()],
        document_type: Annotated[str, Form()]
) -> FileResponse:
    metadata = ThesisMetadata(
        advisors=advisors,
        authors=authors,
        code=code,
        issued=issued,
        abstract=abstract,
        language=language,
        subjects=subjects,
        title=title,
        document_type=document_type
    )
    code = metadata.code
    xml = generate_dublin_core_xml(metadata)
    pdf = edit_pdf(document.file)
    saf_file = build_saf_file(xml, pdf, code)

    return FileResponse(
        path=saf_file,
        filename=f"{code}.zip",
        media_type="application/zip",
        background=BackgroundTask(os.remove, saf_file)
    )


# serve with uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app_ui, port=8000, log_level="info")


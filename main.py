import os
from typing import Annotated

from fastapi import FastAPI, UploadFile, Form
from starlette.background import BackgroundTask
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from dspace import generate_dublin_core_xml, build_saf_file
from dto import ThesisMetadata
from inference import extract_metadata, extract_keywords
from pdf_utils import edit_pdf, extract_page_text

app_ui = FastAPI()
app_api = FastAPI()

static_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "static"))

app_ui.mount("/api/v1", app_api)
app_ui.mount("/", StaticFiles(directory=static_path, html=True), name="static")


@app_api.post("/inferMetadata")
def infer_metadata(document: UploadFile, cover_page: int, abstract_page) -> ThesisMetadata:
    cover_page_text = extract_page_text(document.file, cover_page)
    abstract_text = extract_page_text(document.file, abstract_page)
    # abstract to single line
    abstract_text = " ".join(abstract_text.splitlines())
    # abstract with single spaces
    abstract_text = " ".join(abstract_text.split())

    cover_page_metadata = extract_metadata(cover_page_text)
    keywords = extract_keywords(abstract_text)

    return ThesisMetadata(
        advisors=cover_page_metadata.advisors,
        authors=cover_page_metadata.authors,
        code="",
        issued=cover_page_metadata.issued,
        abstract=abstract_text,
        language="",
        subjects=keywords,
        title=cover_page_metadata.title,
        document_type="",
        thesis_degree_grantor=cover_page_metadata.thesis_degree_grantor,
        thesis_degree_name=""
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
        document_type: Annotated[str, Form()],
        thesis_degree_grantor: Annotated[str, Form()],
        thesis_degree_name: Annotated[str, Form()],
        watermark_start_page: Annotated[int, Form()],
        watermark_end_page: Annotated[int, Form()],
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
        document_type=document_type,
        thesis_degree_grantor=thesis_degree_grantor,
        thesis_degree_name=thesis_degree_name
    )
    code = metadata.code
    xml = generate_dublin_core_xml(metadata)
    pdf = edit_pdf(document.file, watermark_start_page, watermark_end_page)
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

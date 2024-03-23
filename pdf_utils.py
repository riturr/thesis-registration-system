from typing import BinaryIO


def edit_pdf(pdf_document: BinaryIO) -> BinaryIO:
    return pdf_document


def extract_cover_page_and_abstract(pdf: BinaryIO) -> tuple[str, str]:
    return "foo", "bar"
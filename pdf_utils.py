import io
import os
from typing import BinaryIO
from pypdf import PdfWriter, PdfReader
from pdf2image import convert_from_bytes
import configparser
import pytesseract

config = configparser.ConfigParser()
config.read("config.conf")

encryption_password = config["PDF"]["encryption_password"]
watermark_pdf_path = config["PDF"]["watermark_pdf_path"]
copyright_notice_pdf_path = config["PDF"]["copyright_notice_pdf_path"]


def add_watermark(pdf_document: BinaryIO, watermark_start_page: int, watermark_end_page: int) -> BinaryIO:
    if watermark_start_page > watermark_end_page:
        raise ValueError("watermark_start_page must be less than watermark_end_page")
    if watermark_start_page < 1:
        raise ValueError("watermark_start_page must be greater than 0")

    stamp = PdfReader(watermark_pdf_path).pages[0]
    writer = PdfWriter(clone_from=pdf_document)
    for i in range(watermark_start_page - 1, watermark_end_page):
        writer.pages[i].merge_page(stamp)

    file = io.BytesIO()
    writer.write(file)
    file.seek(0)
    return file


def add_copyright_notice(pdf_document: BinaryIO) -> BinaryIO:
    result = io.BytesIO()

    copyright_notice = PdfReader(copyright_notice_pdf_path)
    writer = PdfWriter(clone_from=pdf_document)
    writer.merge(position=1, fileobj=copyright_notice, pages=(0, 1))

    writer.write(result)
    result.seek(0)
    return result


def encrypt_pdf(pdf_document: BinaryIO) -> BinaryIO:
    result = io.BytesIO()

    writer = PdfWriter(clone_from=pdf_document)
    writer.encrypt(encryption_password)

    writer.write(result)
    result.seek(0)
    return result


def edit_pdf(pdf_document: BinaryIO, watermark_start_page: int, watermark_end_page: int) -> BinaryIO:
    pdf_with_watermark = add_watermark(pdf_document, watermark_start_page, watermark_end_page)
    pdf_with_copyright_notice = add_copyright_notice(pdf_with_watermark)
    # pdf_encrypted = encrypt_pdf(pdf_with_copyright_notice)
    return pdf_with_copyright_notice


def extract_page_text(pdf: BinaryIO, page: int) -> str:
    pytesseract.pytesseract.tesseract_cmd = os.path.normpath(os.path.join(os.path.dirname(__file__), "Tesseract-OCR/tesseract.exe"))
    poppler_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "poppler/Library/bin"))
    pdf.seek(0)
    first_page = int(page)
    last_page = int(page) + int(1)
    page_as_image = convert_from_bytes(pdf.read(), first_page=first_page, last_page=last_page, poppler_path=poppler_path)[0]
    return pytesseract.image_to_string(page_as_image)

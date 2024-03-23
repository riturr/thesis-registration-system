import tempfile
import zipfile
from typing import BinaryIO

from lxml import etree as et

from dto import ThesisMetadata


def generate_dublin_core_xml(metadata: ThesisMetadata) -> str:
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <dublin_core schema="dc">
        <dcvalue element="title" qualifier="none">{metadata.title}</dcvalue>
        {"".join(f'<dcvalue element="creator" qualifier="none">{author}</dcvalue>' for author in metadata.authors)}
        {"".join(f'<dcvalue element="contributor" qualifier="none">{advisor}</dcvalue>' for advisor in metadata.advisors)}
        <dcvalue element="date" qualifier="issued">{metadata.issued}</dcvalue>
        <dcvalue element="description" qualifier="abstract">{metadata.abstract}</dcvalue>
        <dcvalue element="language" qualifier="iso">{metadata.language}</dcvalue>
        {"".join(f'<dcvalue element="subject" qualifier="none">{subject}</dcvalue>' for subject in metadata.subjects)}
        <dcvalue element="type" qualifier="none">{metadata.document_type}</dcvalue>
    </dublin_core>
    """

    pretty_xml = et.tostring(et.XML(xml.encode()), pretty_print=True).decode('utf-8')
    return pretty_xml


def build_saf_file(xml: str, pdf: BinaryIO, code: str):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        with zipfile.ZipFile(temp, mode="w") as z:
            z.writestr("item_000/contents", code)
            z.writestr("item_000/dublin_core.xml", xml)
            z.writestr(f"item_000/{code}.pdf", pdf.read())
        temp.seek(0)

        return temp.name
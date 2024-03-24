import tempfile
import zipfile
from typing import BinaryIO

from lxml import etree as et

from dto import ThesisMetadata


def generate_dublin_core_xml(metadata: ThesisMetadata) -> str:
    separator = "\n    "

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<dublin_core>
    <dcvalue element="title" language="es_ES" qualifier="none">{metadata.title}</dcvalue>
    {separator.join(f'<dcvalue element="contributor" qualifier="author">{author}</dcvalue>' for author in metadata.authors)}
    {separator.join(f'<dcvalue element="contributor" qualifier="advisor">{advisor}</dcvalue>' for advisor in metadata.advisors)}
    <dcvalue element="date" qualifier="issued">{metadata.issued}</dcvalue>
    <dcvalue element="description" language="es_ES" qualifier="abstract">{metadata.abstract}</dcvalue>
    <dcvalue element="language" language="es_ES" qualifier="iso">{metadata.language}</dcvalue>
    {separator.join(f'<dcvalue element="subject" language="es_ES" qualifier="none">{subject}</dcvalue>' for subject in metadata.subjects)}
    <dcvalue element="type" language="es_ES" qualifier="none">{metadata.document_type}</dcvalue>
    <dcvalue element="thesisdegreegrantor" language="es_ES" qualifier="none">{metadata.thesis_degree_grantor}</dcvalue>
    <dcvalue element="thesisdegreename" language="es_ES" qualifier="none">{metadata.thesis_degree_name}</dcvalue>
</dublin_core>
"""

    pretty_xml = et.tostring(et.XML(xml.encode()), pretty_print=True).decode('utf-8')
    return pretty_xml


def build_saf_file(xml: str, pdf: BinaryIO, code: str):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        with zipfile.ZipFile(temp, mode="w") as z:
            z.writestr("item_000/contents", f"{code}.pdf")
            z.writestr("item_000/dublin_core.xml", xml)
            z.writestr(f"item_000/{code}.pdf", pdf.read())
        temp.seek(0)

        return temp.name

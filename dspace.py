import io
import tempfile
import zipfile
import configparser
import json
from typing import BinaryIO
from PIL import Image

from lxml import etree as et

from dto import ThesisMetadata


config = configparser.ConfigParser()
config.read("config.conf", encoding="utf-8")
language_mapping = json.loads(config["MARC21XML_TO_DUBLINCORE"]["language_mapping"])


def generate_dublin_core_xml(metadata: ThesisMetadata) -> str:
    language = language_mapping.get(metadata.language, "es_ES")

    separator = "\n    "
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<dublin_core>
    <dcvalue element="title" language="es_ES" qualifier="none">{metadata.title}</dcvalue>
    {separator.join(f'<dcvalue element="contributor" qualifier="author">{author}</dcvalue>' for author in metadata.authors)}
    {separator.join(f'<dcvalue element="contributor" qualifier="advisor">{advisor}</dcvalue>' for advisor in metadata.advisors)}
    <dcvalue element="date" qualifier="issued">{metadata.issued}</dcvalue>
    <dcvalue element="description" language="es_ES" qualifier="abstract">{metadata.abstract}</dcvalue>
    <dcvalue element="language" language="es_ES" qualifier="iso">{language}</dcvalue>
    {separator.join(f'<dcvalue element="subject" language="es_ES" qualifier="none">{subject}</dcvalue>' for subject in metadata.subjects)}
    <dcvalue element="type" language="es_ES" qualifier="none">Thesis</dcvalue>
    <dcvalue element="thesisdegreegrantor" language="es_ES" qualifier="none">{metadata.thesis_degree_grantor}</dcvalue>
    <dcvalue element="thesisdegreename" language="es_ES" qualifier="none">{metadata.thesis_degree_name}</dcvalue>
</dublin_core>
"""

    pretty_xml = et.tostring(et.XML(xml.encode()), pretty_print=True).decode('utf-8')
    return pretty_xml


def build_saf_file(xml: str, pdf: BinaryIO, code: str, thumbnail: Image.Image):

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        with zipfile.ZipFile(temp, mode="w") as z:
            z.writestr("item_000/contents", f"{code}.pdf\nthumbnail.jpg\tbundle:THUMBNAIL")
            z.writestr("item_000/dublin_core.xml", xml)
            z.writestr(f"item_000/{code}.pdf", pdf.read())

            thumbnail_bytes = io.BytesIO()
            thumbnail.save(thumbnail_bytes, format="JPEG")
            z.writestr("item_000/thumbnail.jpg", thumbnail_bytes.getvalue())
        temp.seek(0)

        return temp.name


def parse_marc21(marc21: BinaryIO) -> ThesisMetadata:
    xml = marc21.read().decode("utf-8")
    root = et.XML(xml.encode())
    namespace = "{http://www.loc.gov/MARC21/slim}"

    code = root.find(f"{namespace}datafield[@tag='092']/{namespace}subfield[@code='c']")
    code = code.text if code is not None else "XX-0000"

    title = root.find(f"{namespace}datafield[@tag='245']/{namespace}subfield[@code='a']")
    title = title.text if title is not None else ""

    advisors = [subfield.text for subfield in root.findall(f"{namespace}datafield[@tag='700']/{namespace}subfield[@code='a']") if subfield is not None]

    authors = [subfield.text for subfield in root.findall(f"{namespace}datafield[@tag='100']/{namespace}subfield[@code='a']") if subfield is not None]
    subjects = [subfield.text for subfield in root.findall(f"{namespace}datafield[@tag='653']/{namespace}subfield[@code='a']") if subfield is not None]

    issued = root.find(f"{namespace}datafield[@tag='260']/{namespace}subfield[@code='c']")
    issued = issued.text if issued is not None else ""

    abstract = root.find(f"{namespace}datafield[@tag='520']/{namespace}subfield[@code='a']")
    abstract = abstract.text if abstract is not None else ""

    language = root.find(f"{namespace}datafield[@tag='041']/{namespace}subfield[@code='a']")
    language = language.text if language is not None else ""

    document_type = root.find(f"{namespace}datafield[@tag='942']/{namespace}subfield[@code='c']")
    document_type = document_type.text if document_type is not None else ""

    thesis_degree_grantor = root.find(f"{namespace}datafield[@tag='502']/{namespace}subfield[@code='a']")
    thesis_degree_grantor = thesis_degree_grantor.text if thesis_degree_grantor is not None else ""

    thesis_degree_name = root.find(f"{namespace}datafield[@tag='502']/{namespace}subfield[@code='a']")
    thesis_degree_name = thesis_degree_name.text if thesis_degree_name is not None else ""

    return ThesisMetadata(
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

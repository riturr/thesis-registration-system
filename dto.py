from fastapi import UploadFile
from pydantic import BaseModel


class ThesisMetadata(BaseModel):
    advisors: list[str]
    authors: list[str]
    code: str
    issued: str
    abstract: str
    language: str
    subjects: list[str]
    title: str
    document_type: str


class ThesisMetadataWithDocument(ThesisMetadata):
    document: UploadFile


class CoverPageMetadata(BaseModel):
    title: str
    authors: list[str]
    advisors: list[str]
    issued: str
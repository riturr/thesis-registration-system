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
    thesis_degree_grantor: str
    thesis_degree_name: str


class CoverPageMetadata(BaseModel):
    title: str
    authors: list[str]
    advisors: list[str]
    issued: str
    thesis_degree_grantor: str

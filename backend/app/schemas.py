from datetime import datetime

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_CONTENT_CHARS = 500_000


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str


class DocumentCreate(BaseModel):
    title: str = Field(default="Untitled document", max_length=200)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str | None = Field(default=None, max_length=MAX_CONTENT_CHARS)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    owner: UserOut
    updated_at: datetime


class DocumentOut(DocumentSummary):
    content: str
    is_owner: bool
    shared_with: list[UserOut]


class DocumentList(BaseModel):
    owned: list[DocumentSummary]
    shared: list[DocumentSummary]


class ShareRequest(BaseModel):
    email: str = Field(max_length=255)

    @field_validator("email")
    @classmethod
    def valid_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v):
            raise ValueError("Enter a valid email address")
        return v

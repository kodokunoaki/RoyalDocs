"""Pydantic schemas for handling document routes entities."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator


class DocumentCreate(BaseModel):
    title: str
    doc_type: str = "parchment"
    content: dict[str, Any]

    @field_validator("doc_type")
    @classmethod
    def validate_doc_type(cls, v: str) -> str:
        if v not in ("scroll", "parchment"):
            raise ValueError("doc_type must be 'scroll' or 'parchment'")
        return v


class DocumentPatch(BaseModel):
    title: str | None = None
    content: dict[str, Any] | None = None


class DocumentOut(BaseModel):
    id: uuid.UUID
    title: str
    doc_type: str
    content: dict[str, Any]
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListOut(BaseModel):
    items: list[DocumentOut]
    total: int
    limit: int
    offset: int


class DiffValue(BaseModel):
    old: Any
    new: Any


class DocumentDiff(BaseModel):
    added: dict[str, Any]
    removed: dict[str, Any]
    changed: dict[str, DiffValue]

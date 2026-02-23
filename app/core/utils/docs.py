"""Utilities-helpers for docs routes."""

import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Document
from app.core.schemas.document import DiffValue, DocumentDiff


async def get_own_doc(
    doc_id: uuid.UUID,
    owner_id: uuid.UUID,
    session: AsyncSession,
) -> Document:
    doc = await session.get(Document, doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    if doc.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    return doc


def resolve_path(content: dict, path: str) -> Any:
    keys = path.strip("/").split("/")
    node: Any = content
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Path '{path}' not found in document",
            )
        node = node[key]
    return node


def set_path(content: dict, path: str, value: Any) -> None:
    keys = path.strip("/").split("/")
    node = content
    for key in keys[:-1]:
        if key not in node or not isinstance(node[key], dict):
            node[key] = {}
        node = node[key]
    node[keys[-1]] = value


def delete_path(content: dict, path: str) -> None:
    keys = path.strip("/").split("/")
    node = content
    for key in keys[:-1]:
        if not isinstance(node, dict) or key not in node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Path '{path}' not found in document",
            )
        node = node[key]
    if keys[-1] not in node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Path '{path}' not found in document",
        )
    del node[keys[-1]]


def diff(a: dict[str, Any], b: dict[str, Any], prefix: str = "") -> DocumentDiff:
    added: dict[str, Any] = {}
    removed: dict[str, Any] = {}
    changed: dict[str, DiffValue] = {}

    def full_key(key: str) -> str:
        return f"{prefix}{key}" if not prefix else f"{prefix}/{key}"

    all_keys = a.keys() | b.keys()

    for key in all_keys:
        fk = full_key(key)
        in_a, in_b = key in a, key in b

        if in_a and not in_b:
            removed[fk] = a[key]
        elif in_b and not in_a:
            added[fk] = b[key]
        elif isinstance(a[key], dict) and isinstance(b[key], dict):
            nested = diff(a[key], b[key], prefix=fk)
            added.update(nested.added)
            removed.update(nested.removed)
            changed.update(nested.changed)
        elif a[key] != b[key]:
            changed[fk] = DiffValue(old=a[key], new=b[key])

    return DocumentDiff(added=added, removed=removed, changed=changed)

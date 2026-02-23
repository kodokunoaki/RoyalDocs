"""Routes for document operations, including:
- CRUD operations,
- json path navigation,
- getting doc difference.
"""

import copy
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Query, status
from sqlalchemy import select, func

from app.api.deps import SessionDep, CurrentUser
from app.core.models import Document
from app.core.schemas.document import (
    DocumentCreate,
    DocumentOut,
    DocumentPatch,
    DocumentListOut,
    DocumentDiff,
)
from app.core.utils import docs as utils

router = APIRouter(prefix="/docs", tags=["Documents"])


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def create_document(
    body: DocumentCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> DocumentOut:
    doc = Document(
        title=body.title,
        doc_type=body.doc_type,
        content=body.content,
        owner_id=current_user.id,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.get("", response_model=DocumentListOut)
async def list_documents(
    session: SessionDep,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> DocumentListOut:
    count_q = (
        select(func.count())
        .select_from(Document)
        .where(Document.owner_id == current_user.id)
    )
    total = (await session.execute(count_q)).scalar_one()

    docs_q = (
        select(Document)
        .where(Document.owner_id == current_user.id)
        .order_by(Document.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    docs = (await session.execute(docs_q)).scalars().all()

    return DocumentListOut(
        items=[DocumentOut.model_validate(d) for d in docs],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/diff", response_model=DocumentDiff)
async def diff_documents(
    session: SessionDep,
    current_user: CurrentUser,
    a: uuid.UUID = Query(..., description="First document ID"),
    b: uuid.UUID = Query(..., description="Second document ID"),
) -> DocumentDiff:
    doc_a = await utils.get_own_doc(a, current_user.id, session)
    doc_b = await utils.get_own_doc(b, current_user.id, session)
    return utils.diff(doc_a.content, doc_b.content)


@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(
    doc_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> DocumentOut:
    doc = await utils.get_own_doc(doc_id, current_user.id, session)
    return DocumentOut.model_validate(doc)


@router.patch("/{doc_id}", response_model=DocumentOut)
async def patch_document(
    doc_id: uuid.UUID,
    body: DocumentPatch,
    session: SessionDep,
    current_user: CurrentUser,
) -> DocumentOut:
    doc = await utils.get_own_doc(doc_id, current_user.id, session)

    if body.title is not None:
        doc.title = body.title
    if body.content is not None:
        doc.content = body.content

    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    doc = await utils.get_own_doc(doc_id, current_user.id, session)
    await session.delete(doc)
    await session.commit()


@router.get("/{doc_id}/path")
async def get_by_path(
    doc_id: uuid.UUID,
    key: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    doc = await utils.get_own_doc(doc_id, current_user.id, session)
    return utils.resolve_path(doc.content, key)


@router.patch("/{doc_id}/path", response_model=DocumentOut)
async def patch_by_path(
    doc_id: uuid.UUID,
    key: str,
    body: dict[str, Any],
    session: SessionDep,
    current_user: CurrentUser,
) -> DocumentOut:
    doc = await utils.get_own_doc(doc_id, current_user.id, session)
    content = copy.deepcopy(doc.content)
    utils.set_path(content, key, body)
    doc.content = content
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.delete("/{doc_id}/path", response_model=DocumentOut)
async def delete_by_path(
    doc_id: uuid.UUID,
    key: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> DocumentOut:
    doc = await utils.get_own_doc(doc_id, current_user.id, session)
    content = copy.deepcopy(doc.content)
    utils.delete_path(content, key)
    doc.content = content
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return DocumentOut.model_validate(doc)

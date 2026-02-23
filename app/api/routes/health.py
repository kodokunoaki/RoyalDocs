"""Health endpoint for application."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    return {"status": "ok"}

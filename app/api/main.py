"""Main API router of project."""

from fastapi import APIRouter

from app.api.routes import auth, docs, health

api_v1_router = APIRouter()
api_v1_router.include_router(auth.router)
api_v1_router.include_router(docs.router)
api_v1_router.include_router(health.router)

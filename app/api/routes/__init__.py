"""Main API router for docs, auth and health handling routes."""

from app.api.routes import auth, docs, health

__all__ = ["auth", "docs", "health"]

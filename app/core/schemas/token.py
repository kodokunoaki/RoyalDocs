"""Pydantic schemas for JWT token handling."""

import uuid

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    type: str = "bearer"


class TokenPayload(BaseModel):
    sub: uuid.UUID | None = None
    exp: int
    jti: uuid.UUID | None = None

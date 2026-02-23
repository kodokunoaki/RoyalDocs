"""Dependency injection utilities for FastAPI routes, including:
- session management,
- user authentication via token.
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app.core.config import settings
from app.core.db import get_session
from app.core.models import User
from app.core.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth")

SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(
    session: SessionDep,
    token: TokenDep,
) -> JSONResponse:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from e
    user = await session.get(User, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

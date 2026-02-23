"""Authentication route for user login via OAuth2 form in FastAPI.
Handles token generation and user validation.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep
from app.core.config import settings
from app.core.crud import user as crud
from app.core.security import create_access_token
from app.core.schemas.token import Token

router = APIRouter(tags=["Auth"])


@router.post("/auth")
async def login(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required.",
        )

    user = await crud.authenticate(
        session=session, username=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user."
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.id, expires_delta=access_token_expires)

    return Token(access_token=access_token, type="bearer")

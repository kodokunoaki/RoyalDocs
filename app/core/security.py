"""Security utilities for password hashing and JWT token creation."""

import uuid
from datetime import timedelta, datetime, timezone

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings

pwd_hash = PasswordHash([BcryptHasher()])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_hash.hash(password)


def create_access_token(
    subject: str, expires_delta: timedelta = timedelta(minutes=15)
) -> str:
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "jti": jti}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

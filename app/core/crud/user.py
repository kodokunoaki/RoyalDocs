"""CRUD operations for managing authentication logic."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app.core.models import User
from app.core.security import verify_password


async def get_user_by_username(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return await session.scalar(statement)


async def authenticate(session: Session, username: str, password: str) -> User | None:
    db_user = await get_user_by_username(session=session, username=username)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user

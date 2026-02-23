"""Database configuration and session dependency."""

import logging
from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.core.models import User

logger = logging.getLogger(settings.PROJECT_NAME)

engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def init_superuser() -> None:

    async with async_session() as session:
        existing = await session.execute(
            select(User).where(User.username == settings.FIRST_SUPERUSER_NAME)
        )
        if existing.scalar_one_or_none():
            logger.debug(
                "Superuser '%s' already exists, skipping.",
                settings.FIRST_SUPERUSER_NAME,
            )
            return

        superuser = User(
            username=settings.FIRST_SUPERUSER_NAME,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            is_active=True,
        )
        session.add(superuser)
        await session.commit()
        logger.info("Superuser '%s' created.", settings.FIRST_SUPERUSER_NAME)

"""Utilities for syncronization task."""

import asyncio
import logging

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import async_session
from app.core.models import Document

logger = logging.getLogger(settings.PROJECT_NAME)


async def sync_loop() -> None:
    while True:
        try:
            async with async_session() as session:
                await run_sync_once(session)
        except asyncio.CancelledError:
            logger.info("Sync loop cancelled, shutting down.")
            raise
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception(
                "Sync task failed, will retry in %s s.",
                settings.SYNC_INTERVAL_SECONDS,
            )
        await asyncio.sleep(settings.SYNC_INTERVAL_SECONDS)


async def _fetch_payload() -> dict:
    """Fetch JSON payload from the configured external URL."""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(settings.SYNC_URL)
        response.raise_for_status()
        payload = response.json()

    if not isinstance(payload, dict):
        logger.warning(
            "Sync URL returned %s instead of a JSON object, skipping.",
            type(payload).__name__,
        )
        return {}

    return payload


async def run_sync_once(session: AsyncSession) -> None:
    """Merge external payload into the root of every document."""
    try:
        payload = await _fetch_payload()
    except httpx.HTTPStatusError as e:
        logger.warning(
            "Sync HTTP error %s from %s, skipping.",
            e.response.status_code,
            settings.SYNC_URL,
        )
        return
    except httpx.RequestError as e:
        logger.warning("Sync request failed (%s), skipping.", e)
        return

    if not payload:
        return

    result = await session.execute(select(Document))
    docs = result.scalars().all()

    if not docs:
        logger.debug("No documents to sync.")
        return

    for doc in docs:
        doc.content = {**doc.content, **payload}

    await session.commit()
    logger.info(
        "Sync complete: merged %d key(s) into %d document(s).",
        len(payload),
        len(docs),
    )

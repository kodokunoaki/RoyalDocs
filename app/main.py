"""FastAPI application factory and startup configuration, including:
- Logging setup
- CORS middleware
- Database schema initialization
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import uvicorn
import yaml
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_v1_router
from app.core.config import settings
from app.core.db import init_superuser
from app.core.logging import setup_logger
from app.core.utils.sync import sync_loop

logger = logging.getLogger(settings.PROJECT_NAME)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await init_superuser()
    logger.info(
        "Starting background sync task (interval: %s s).",
        settings.SYNC_INTERVAL_SECONDS,
    )
    sync_task = asyncio.create_task(sync_loop())
    try:
        yield
    finally:
        sync_task.cancel()
        try:
            await sync_task
        except asyncio.CancelledError:
            pass
        logger.info("Background sync task stopped.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    fastapi_app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

    # Set all CORS enabled origins
    if settings.all_cors_origins:
        fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.all_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    fastapi_app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return fastapi_app


app = create_app()


async def main() -> None:

    setup_logger(settings.PROJECT_NAME, f"{settings.PROJECT_NAME}.log")

    log_cfg_path = Path("logging.yaml")
    log_config = yaml.safe_load(log_cfg_path.read_text(encoding="utf-8"))

    config = uvicorn.Config(
        app=app,
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        log_config=log_config,
        log_level=settings.UVICORN_LOG_LEVEL,
        workers=settings.UVICORN_WORKERS,
        limit_concurrency=settings.UVICORN_LIMIT_CONCURRENCY,
    )

    server = uvicorn.Server(config)

    logger.info(
        "Starting server on %s:%s", settings.UVICORN_HOST, settings.UVICORN_PORT
    )

    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")

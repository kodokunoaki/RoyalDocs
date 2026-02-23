"""Application configuration using Pydantic-based settings.
Includes environment-specific values, CORS, PostgreSQL and JWT parameters.
"""

from typing import Literal, List, Union, Any, Annotated

from pydantic import BeforeValidator, AnyUrl, computed_field
from pydantic_settings import BaseSettings


def parse_cors(value: Any) -> Union[List[str], str]:
    if isinstance(value, str) and not value.startswith("["):
        return [i.strip() for i in value.split(",")]
    if isinstance(value, list | str):
        return value
    raise ValueError(value)


class Settings(BaseSettings):
    """Main application settings loaded from environment variables or .env file.

    Contains:
    - Project meta info
    - CORS settings
    - Database parameters
    - JWT parameters
    """

    PROJECT_NAME: str = "RoyalDocs"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    INSTANCE_ID: str
    HOST_ID: str
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field
    @property
    def all_cors_origins(self) -> List[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]

    UVICORN_HOST: str
    UVICORN_PORT: int
    UVICORN_LOG_LEVEL: str
    UVICORN_WORKERS: int
    UVICORN_LIMIT_CONCURRENCY: int

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5

    SYNC_URL: str = "https://example.com/api/data"
    SYNC_INTERVAL_SECONDS: int = 30

    FIRST_SUPERUSER_NAME: str = "test"
    FIRST_SUPERUSER_PASSWORD: str = "test"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()

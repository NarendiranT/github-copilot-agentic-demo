"""Application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime configuration; `DATABASE_URL` overrides the default."""

    database_url: str = "sqlite+aiosqlite:///./db.sqlite3"


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()

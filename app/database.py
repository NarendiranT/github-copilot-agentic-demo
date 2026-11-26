"""Async SQLAlchemy engine, session and schema setup."""

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def create_engine(database_url: str) -> AsyncEngine:
    """Create an async engine for the given database URL."""
    return create_async_engine(database_url)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create a session factory whose objects stay readable after commit."""
    return async_sessionmaker(engine, expire_on_commit=False)


async def init_db(engine: AsyncEngine) -> None:
    """Create any missing tables."""
    # Imported so the models register on Base.metadata.
    from app import models  # noqa: F401

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield a session bound to the application's session factory."""
    async with request.app.state.session_factory() as session:
        yield session

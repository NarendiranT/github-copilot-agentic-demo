"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.blogs import router as blogs_router
from app.config import get_settings
from app.database import create_engine, create_session_factory, init_db
from app.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Open the database on startup and dispose of it on shutdown."""
    engine = create_engine(get_settings().database_url)
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    try:
        await init_db(engine)
        yield
    finally:
        await engine.dispose()


app = FastAPI(title="GitHub Copilot Agentic Demo", version="0.1.0", lifespan=lifespan)
app.include_router(health_router)
app.include_router(blogs_router)

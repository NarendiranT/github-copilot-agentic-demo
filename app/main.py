"""FastAPI application entry point."""

from fastapi import FastAPI

from app.health import router as health_router

app = FastAPI(title="GitHub Copilot Agentic Demo", version="0.1.0")
app.include_router(health_router)

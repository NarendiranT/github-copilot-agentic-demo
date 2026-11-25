"""Health check endpoint."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Response body returned by the health check."""

    status: Literal["healthy"]


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=200,
    tags=["health"],
    summary="Application health check",
)
async def health() -> HealthResponse:
    """Report that the application is running.

    Requires no authentication and performs no external calls.
    """
    return HealthResponse(status="healthy")

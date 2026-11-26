"""Blog CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import blog_service
from app.database import get_session
from app.models import Blog
from app.schemas import BlogCreate, BlogRead, BlogUpdate

router = APIRouter(prefix="/blogs", tags=["blogs"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
# Upper bound keeps ids within SQLite's signed 64-bit integer range.
BlogId = Annotated[int, Path(gt=0, le=2**63 - 1, description="Blog identifier")]
NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "Blog not found"}}


def _found(blog: Blog | None) -> Blog:
    if blog is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Blog not found")
    return blog


@router.post(
    "",
    response_model=BlogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a blog",
)
async def create_blog(data: BlogCreate, session: SessionDep) -> Blog:
    """Create a blog from a non-blank title and content."""
    return await blog_service.create_blog(session, data)


@router.get(
    "",
    response_model=list[BlogRead],
    status_code=status.HTTP_200_OK,
    summary="List blogs",
)
async def list_blogs(session: SessionDep) -> list[Blog]:
    """List all blogs ordered by id."""
    return await blog_service.list_blogs(session)


@router.get(
    "/{blog_id}",
    response_model=BlogRead,
    status_code=status.HTTP_200_OK,
    summary="Get a blog",
    responses=NOT_FOUND,
)
async def get_blog(blog_id: BlogId, session: SessionDep) -> Blog:
    """Return a single blog by id."""
    return _found(await blog_service.get_blog(session, blog_id))


@router.patch(
    "/{blog_id}",
    response_model=BlogRead,
    status_code=status.HTTP_200_OK,
    summary="Update a blog",
    responses=NOT_FOUND,
)
async def update_blog(blog_id: BlogId, data: BlogUpdate, session: SessionDep) -> Blog:
    """Update only the supplied fields of a blog."""
    return _found(await blog_service.update_blog(session, blog_id, data))


@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a blog",
    responses=NOT_FOUND,
)
async def delete_blog(blog_id: BlogId, session: SessionDep) -> Response:
    """Delete a blog by id."""
    _found(await blog_service.delete_blog(session, blog_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)

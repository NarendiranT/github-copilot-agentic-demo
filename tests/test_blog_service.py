"""Service-layer tests, independent of HTTP."""

from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app import blog_service
from app.database import create_engine, create_session_factory, init_db
from app.schemas import BlogCreate, BlogUpdate


@pytest.fixture
async def session(isolated_database: str) -> AsyncIterator[AsyncSession]:
    engine = create_engine(isolated_database)
    await init_db(engine)
    async with create_session_factory(engine)() as db_session:
        yield db_session
    await engine.dispose()


async def test_create_then_get_returns_blog(session: AsyncSession) -> None:
    created = await blog_service.create_blog(
        session, BlogCreate(title="T", content="C")
    )

    fetched = await blog_service.get_blog(session, created.id)

    assert fetched is not None
    assert fetched.title == "T"
    assert created.created_at == created.updated_at


async def test_get_update_delete_missing_return_none(session: AsyncSession) -> None:
    assert await blog_service.get_blog(session, 1) is None
    assert await blog_service.update_blog(session, 1, BlogUpdate(title="x")) is None
    assert await blog_service.delete_blog(session, 1) is None


async def test_update_leaves_unsupplied_fields(session: AsyncSession) -> None:
    created = await blog_service.create_blog(
        session, BlogCreate(title="T", content="C")
    )

    updated = await blog_service.update_blog(session, created.id, BlogUpdate(title="N"))

    assert updated is not None
    assert (updated.title, updated.content) == ("N", "C")
    assert updated.updated_at >= updated.created_at


async def test_list_is_ordered_by_id(session: AsyncSession) -> None:
    for title in ("a", "b", "c"):
        await blog_service.create_blog(session, BlogCreate(title=title, content="x"))

    blogs = await blog_service.list_blogs(session)

    assert [blog.title for blog in blogs] == ["a", "b", "c"]

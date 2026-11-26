"""Blog persistence operations, independent of HTTP."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Blog, utc_now
from app.schemas import BlogCreate, BlogUpdate


async def create_blog(session: AsyncSession, data: BlogCreate) -> Blog:
    """Persist a new blog with equal created and updated timestamps."""
    now = utc_now()
    blog = Blog(title=data.title, content=data.content, created_at=now, updated_at=now)
    session.add(blog)
    await session.commit()
    return blog


async def list_blogs(session: AsyncSession) -> list[Blog]:
    """Return all blogs ordered by id ascending."""
    result = await session.scalars(select(Blog).order_by(Blog.id))
    return list(result)


async def get_blog(session: AsyncSession, blog_id: int) -> Blog | None:
    """Return the blog with the given id, or None if it does not exist."""
    return await session.get(Blog, blog_id)


async def update_blog(
    session: AsyncSession, blog_id: int, data: BlogUpdate
) -> Blog | None:
    """Apply the supplied fields; return None if the blog does not exist."""
    blog = await session.get(Blog, blog_id)
    if blog is None:
        return None
    for name, value in data.model_dump(exclude_unset=True).items():
        setattr(blog, name, value)
    blog.updated_at = utc_now()
    await session.commit()
    return blog


async def delete_blog(session: AsyncSession, blog_id: int) -> Blog | None:
    """Delete the blog; return None if it does not exist."""
    blog = await session.get(Blog, blog_id)
    if blog is None:
        return None
    await session.delete(blog)
    await session.commit()
    return blog

"""ORM models."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from app.database import Base


class UTCDateTime(TypeDecorator[datetime]):
    """Store UTC datetimes; SQLite drops tzinfo, so re-attach it on load."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Naive datetimes are not allowed")
        return value.astimezone(UTC)

    def process_result_value(self, value: datetime | None, dialect: Dialect):
        if value is None:
            return None
        return value.replace(tzinfo=UTC)


def utc_now() -> datetime:
    """Return the current time as a UTC-aware datetime."""
    return datetime.now(UTC)


class Blog(Base):
    """A blog post."""

    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)

"""Shared fixtures."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from app.config import get_settings


@pytest.fixture(autouse=True)
def isolated_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """Point every test at its own SQLite file instead of ./db.sqlite3."""
    url = f"sqlite+aiosqlite:///{tmp_path / 'test.sqlite3'}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    yield url
    get_settings.cache_clear()

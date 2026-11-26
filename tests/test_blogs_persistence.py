"""Blogs must survive an application restart on the same database."""

from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.config import get_settings
from app.main import app

BLOGS = "/blogs"


def test_created_blog_survives_restart_with_same_timestamps() -> None:
    with TestClient(app) as first:
        created = first.post(BLOGS, json={"title": "T", "content": "C"}).json()

    with TestClient(app) as second:
        reloaded = second.get(f"{BLOGS}/{created['id']}").json()

    assert reloaded == created
    assert datetime.fromisoformat(reloaded["created_at"]).tzinfo is not None
    assert reloaded["created_at"] == reloaded["updated_at"]


def test_patch_survives_restart() -> None:
    with TestClient(app) as first:
        created = first.post(BLOGS, json={"title": "T", "content": "C"}).json()
        patched = first.patch(f"{BLOGS}/{created['id']}", json={"title": "T2"}).json()

    with TestClient(app) as second:
        reloaded = second.get(f"{BLOGS}/{created['id']}").json()

    assert reloaded == patched
    assert reloaded["content"] == "C"


def test_delete_survives_restart() -> None:
    with TestClient(app) as first:
        created = first.post(BLOGS, json={"title": "T", "content": "C"}).json()
        assert first.delete(f"{BLOGS}/{created['id']}").status_code == 204

    with TestClient(app) as second:
        assert second.get(f"{BLOGS}/{created['id']}").status_code == 404
        assert second.get(BLOGS).json() == []


def test_multiple_blogs_and_order_survive_restart() -> None:
    with TestClient(app) as first:
        created = [
            first.post(BLOGS, json={"title": t, "content": "C"}).json()
            for t in ("a", "b", "c")
        ]

    with TestClient(app) as second:
        assert second.get(BLOGS).json() == created


def test_database_url_selects_the_database_file(
    isolated_database: str, tmp_path: Path
) -> None:
    db_file = tmp_path / "test.sqlite3"
    assert not db_file.exists()

    with TestClient(app) as client:
        client.post(BLOGS, json={"title": "T", "content": "C"})

    assert db_file.exists()


def test_different_database_url_does_not_see_other_data(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    with TestClient(app) as first:
        first.post(BLOGS, json={"title": "T", "content": "C"})

    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path / 'other.db'}")
    get_settings.cache_clear()

    with TestClient(app) as second:
        assert second.get(BLOGS).json() == []


def test_default_database_url_is_local_sqlite(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL")
    get_settings.cache_clear()

    assert get_settings().database_url == "sqlite+aiosqlite:///./db.sqlite3"

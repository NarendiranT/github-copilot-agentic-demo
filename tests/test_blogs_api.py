"""Tests for the blog CRUD API (GitHub issue #5)."""

from collections.abc import Iterator
from datetime import datetime

from fastapi.testclient import TestClient
import pytest

from app.main import app

BLOGS = "/blogs"


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def create(client: TestClient, title: str = "Title", content: str = "Body") -> dict:
    response = client.post(BLOGS, json={"title": title, "content": content})
    assert response.status_code == 201
    return response.json()


# Create


def test_create_returns_201_with_all_fields(client: TestClient) -> None:
    response = client.post(BLOGS, json={"title": "Hello", "content": "World"})

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "title", "content", "created_at", "updated_at"}
    assert isinstance(body["id"], int)
    assert body["title"] == "Hello"
    assert body["content"] == "World"


def test_create_sets_equal_timezone_aware_timestamps(client: TestClient) -> None:
    body = create(client)

    created = datetime.fromisoformat(body["created_at"])
    assert created.tzinfo is not None
    assert body["created_at"] == body["updated_at"]


def test_create_assigns_unique_ids(client: TestClient) -> None:
    assert create(client)["id"] != create(client)["id"]


def test_create_strips_surrounding_whitespace(client: TestClient) -> None:
    body = create(client, title="  Hi  ", content="\n body \t")

    assert body["title"] == "Hi"
    assert body["content"] == "body"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": "T"},
        {"content": "C"},
        {"title": "", "content": "C"},
        {"title": "T", "content": ""},
        {"title": "   ", "content": "C"},
        {"title": "T", "content": " \n\t "},
        {"title": None, "content": "C"},
        {"title": "T", "content": None},
        {"title": 123, "content": "C"},
        {"title": "T", "content": ["x"]},
        {"title": "T", "content": "C", "id": 5},
    ],
)
def test_create_invalid_payload_returns_422(client: TestClient, payload: dict) -> None:
    assert client.post(BLOGS, json=payload).status_code == 422
    assert client.get(BLOGS).json() == []


# Read


def test_list_returns_200_and_empty_list_initially(client: TestClient) -> None:
    response = client.get(BLOGS)

    assert response.status_code == 200
    assert response.json() == []


def test_list_returns_blogs_ordered_by_id(client: TestClient) -> None:
    first = create(client, title="A")
    second = create(client, title="B")

    response = client.get(BLOGS)

    assert response.status_code == 200
    assert response.json() == [first, second]


def test_get_returns_blog(client: TestClient) -> None:
    created = create(client)

    response = client.get(f"{BLOGS}/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


# Update


def test_patch_updates_only_supplied_title(client: TestClient) -> None:
    created = create(client, title="Old", content="Keep")

    response = client.patch(f"{BLOGS}/{created['id']}", json={"title": " New "})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "New"
    assert body["content"] == "Keep"
    assert body["created_at"] == created["created_at"]
    assert body["updated_at"] >= created["updated_at"]


def test_patch_updates_only_supplied_content(client: TestClient) -> None:
    created = create(client, title="Keep", content="Old")

    body = client.patch(f"{BLOGS}/{created['id']}", json={"content": "New"}).json()

    assert body["title"] == "Keep"
    assert body["content"] == "New"


def test_patch_updates_both_fields_and_persists(client: TestClient) -> None:
    created = create(client)

    client.patch(f"{BLOGS}/{created['id']}", json={"title": "T2", "content": "C2"})

    fetched = client.get(f"{BLOGS}/{created['id']}").json()
    assert (fetched["title"], fetched["content"]) == ("T2", "C2")
    assert fetched["created_at"] == created["created_at"]


def test_patch_advances_updated_at_when_clock_moves(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    created = create(client)
    later = datetime.fromisoformat(created["created_at"]).replace(year=2999)
    monkeypatch.setattr("app.blog_service.utc_now", lambda: later)

    body = client.patch(f"{BLOGS}/{created['id']}", json={"title": "X"}).json()

    assert datetime.fromisoformat(body["updated_at"]) == later
    assert body["created_at"] == created["created_at"]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": None},
        {"content": None},
        {"title": "ok", "content": None},
        {"title": ""},
        {"title": "   "},
        {"content": " \n"},
        {"title": 5},
        {"unknown": "x"},
        {"title": "ok", "id": 9},
        {"created_at": "2020-01-01T00:00:00Z"},
    ],
)
def test_patch_invalid_payload_returns_422_and_changes_nothing(
    client: TestClient, payload: dict
) -> None:
    created = create(client)

    response = client.patch(f"{BLOGS}/{created['id']}", json=payload)

    assert response.status_code == 422
    assert client.get(f"{BLOGS}/{created['id']}").json() == created


def test_patch_whitespace_only_title_keeps_stored_value_and_timestamp(
    client: TestClient,
) -> None:
    created = create(client)

    assert (
        client.patch(f"{BLOGS}/{created['id']}", json={"title": " "}).status_code == 422
    )

    fetched = client.get(f"{BLOGS}/{created['id']}").json()
    assert fetched["updated_at"] == created["updated_at"]


def test_patch_missing_blog_with_invalid_body_returns_422(client: TestClient) -> None:
    assert client.patch(f"{BLOGS}/999", json={}).status_code == 422


def test_patch_does_not_change_other_blogs(client: TestClient) -> None:
    first = create(client, title="A")
    second = create(client, title="B")

    client.patch(f"{BLOGS}/{first['id']}", json={"title": "A2"})

    assert client.get(f"{BLOGS}/{second['id']}").json() == second


def test_list_stays_ordered_by_id_after_update_and_delete(client: TestClient) -> None:
    ids = [create(client, title=t)["id"] for t in ("a", "b", "c")]
    client.patch(f"{BLOGS}/{ids[0]}", json={"title": "a2"})
    client.delete(f"{BLOGS}/{ids[1]}")

    listed = client.get(BLOGS).json()

    assert [blog["id"] for blog in listed] == [ids[0], ids[2]]
    assert [blog["title"] for blog in listed] == ["a2", "c"]


def test_create_accepts_long_and_unicode_text(client: TestClient) -> None:
    content = "é漢字🙂" * 5000

    body = create(client, title="Ünï 🙂", content=content)

    assert client.get(f"{BLOGS}/{body['id']}").json()["content"] == content


# Delete


def test_delete_returns_204_with_empty_body_then_404(client: TestClient) -> None:
    created = create(client)

    response = client.delete(f"{BLOGS}/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"{BLOGS}/{created['id']}").status_code == 404
    assert client.get(BLOGS).json() == []
    assert client.delete(f"{BLOGS}/{created['id']}").status_code == 404


# Missing and invalid ids


@pytest.mark.parametrize("method", ["GET", "PATCH", "DELETE"])
def test_missing_blog_returns_404(client: TestClient, method: str) -> None:
    kwargs = {"json": {"title": "x"}} if method == "PATCH" else {}

    response = client.request(method, f"{BLOGS}/999", **kwargs)

    assert response.status_code == 404
    assert response.json() == {"detail": "Blog not found"}


@pytest.mark.parametrize("method", ["GET", "PATCH", "DELETE"])
def test_largest_supported_id_returns_404_not_error(
    client: TestClient, method: str
) -> None:
    kwargs = {"json": {"title": "x"}} if method == "PATCH" else {}

    response = client.request(method, f"{BLOGS}/{2**63 - 1}", **kwargs)

    assert response.status_code == 404


@pytest.mark.parametrize(
    "blog_id", ["abc", "0", "-1", "1.5", "1e3", str(2**63), str(2**200)]
)
@pytest.mark.parametrize("method", ["GET", "PATCH", "DELETE"])
def test_invalid_id_returns_422(client: TestClient, method: str, blog_id: str) -> None:
    kwargs = {"json": {"title": "x"}} if method == "PATCH" else {}

    response = client.request(method, f"{BLOGS}/{blog_id}", **kwargs)

    assert response.status_code == 422


# OpenAPI / Swagger


def test_openapi_documents_blog_operations(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert set(paths["/blogs"]) == {"get", "post"}
    assert set(paths["/blogs/{blog_id}"]) == {"get", "patch", "delete"}
    assert "201" in paths["/blogs"]["post"]["responses"]
    assert "204" in paths["/blogs/{blog_id}"]["delete"]["responses"]
    assert "404" in paths["/blogs/{blog_id}"]["get"]["responses"]
    assert "422" in paths["/blogs"]["post"]["responses"]


def test_openapi_blog_schemas_match_contract(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    schemas = spec["components"]["schemas"]
    paths = spec["paths"]

    assert set(schemas["BlogRead"]["required"]) == {
        "id",
        "title",
        "content",
        "created_at",
        "updated_at",
    }
    assert set(schemas["BlogCreate"]["required"]) == {"title", "content"}
    assert "required" not in schemas["BlogUpdate"]
    assert schemas["BlogCreate"]["additionalProperties"] is False
    assert schemas["BlogUpdate"]["additionalProperties"] is False
    assert set(paths["/blogs"]["post"]["requestBody"]["content"]) == {
        "application/json"
    }
    for method in ("get", "patch", "delete"):
        assert "404" in paths["/blogs/{blog_id}"][method]["responses"]
        assert "422" in paths["/blogs/{blog_id}"][method]["responses"]
    assert "200" in paths["/blogs"]["get"]["responses"]
    assert "200" in paths["/blogs/{blog_id}"]["patch"]["responses"]


def test_swagger_ui_is_served(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200

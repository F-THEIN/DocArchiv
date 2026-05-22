"""Tests fuer Tag-API und Tag-Schemas."""

from fastapi.testclient import TestClient
from pydantic import ValidationError

from domain.schemas import TagCreate
from tests.conftest import FakeTagService


def test_list_tags_returns_counts(client: TestClient) -> None:
    """Die Tag-Liste liefert Tags inklusive Dokumentanzahl."""
    response = client.get("/api/tags")

    assert response.status_code == 200
    payload = response.json()
    assert payload == [
        {"id": 1, "name": "rechnung", "color": "#003B7E", "document_count": 2},
        {"id": 2, "name": "stadtwerke", "color": None, "document_count": 1},
    ]


def test_create_tag_normalizes_name_and_color(client: TestClient) -> None:
    """Die Tag-Anlage normalisiert Name und Farbe."""
    response = client.post("/api/tags", json={"name": " Haus ", "color": " #00A550 "})

    assert response.status_code == 201
    assert response.json() == {"id": 3, "name": "haus", "color": "#00A550", "document_count": 0}


def test_create_existing_tag_returns_existing_tag(client: TestClient) -> None:
    """Ein vorhandener Tag wird idempotent zurueckgegeben."""
    response = client.post("/api/tags", json={"name": " Rechnung "})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "rechnung", "color": "#003B7E", "document_count": 2}


def test_create_tag_rejects_blank_name(client: TestClient) -> None:
    """Leere Tag-Namen erzeugen einen Validierungsfehler."""
    response = client.post("/api/tags", json={"name": "   "})

    assert response.status_code == 422


def test_get_tag_returns_tag(client: TestClient) -> None:
    """Ein vorhandener Tag kann per ID geladen werden."""
    response = client.get("/api/tags/1")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "rechnung", "color": "#003B7E", "document_count": 2}


def test_get_tag_returns_404_for_missing_tag(client: TestClient) -> None:
    """Fehlende Tags werden als HTTP 404 abgebildet."""
    response = client.get("/api/tags/999")

    assert response.status_code == 404
    assert "Tag mit ID 999" in response.json()["detail"]


def test_delete_tag_removes_tag(client: TestClient, fake_tag_service: FakeTagService) -> None:
    """Ein vorhandener Tag kann geloescht werden."""
    response = client.delete("/api/tags/2")

    assert response.status_code == 204
    assert fake_tag_service.deleted_tag_ids == [2]


def test_delete_tag_returns_404_for_missing_tag(client: TestClient) -> None:
    """Loeschen eines fehlenden Tags liefert HTTP 404."""
    response = client.delete("/api/tags/999")

    assert response.status_code == 404
    assert "Tag mit ID 999" in response.json()["detail"]


def test_tag_create_schema_normalizes_name_and_color() -> None:
    """Das TagCreate-Schema normalisiert Name und Farbe."""
    schema = TagCreate(name=" Rechnung ", color=" #003B7E ")

    assert schema.name == "rechnung"
    assert schema.color == "#003B7E"


def test_tag_create_schema_rejects_blank_name() -> None:
    """Das TagCreate-Schema verhindert blanke Namen."""
    try:
        TagCreate(name="   ")
    except ValidationError as exc:
        assert "Tag-Name darf nicht leer sein" in str(exc)
    else:
        raise AssertionError("ValidationError wurde erwartet.")

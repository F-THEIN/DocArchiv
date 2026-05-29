"""Tests fuer Dokumenttyp-API."""

from fastapi.testclient import TestClient

from tests.conftest import FakeDocumentTypeService


def test_list_document_types(client: TestClient) -> None:
    """Dokumenttypen werden als Liste mit Dokumentanzahl geliefert."""
    response = client.get("/api/document-types")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["name"] == "Rechnung"
    assert payload[0]["document_count"] == 1


def test_create_document_type(client: TestClient) -> None:
    """Ein neuer Dokumenttyp kann angelegt werden."""
    response = client.post("/api/document-types", json={"name": "Antrag", "color": "#FF5722"})

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Antrag"
    assert payload["color"] == "#FF5722"
    assert payload["document_count"] == 0


def test_create_document_type_returns_existing(client: TestClient) -> None:
    """Ein vorhandener Dokumenttyp wird zurueckgegeben statt doppelt angelegt."""
    response = client.post("/api/document-types", json={"name": "Rechnung"})

    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_get_document_type(client: TestClient) -> None:
    """Ein Dokumenttyp kann per ID geladen werden."""
    response = client.get("/api/document-types/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Rechnung"


def test_get_document_type_returns_404(client: TestClient) -> None:
    """Fehlende Dokumenttypen liefern HTTP 404."""
    response = client.get("/api/document-types/999")

    assert response.status_code == 404
    assert "Dokumenttyp mit ID 999" in response.json()["detail"]


def test_update_document_type(client: TestClient) -> None:
    """Ein Dokumenttyp kann umbenannt werden."""
    response = client.patch("/api/document-types/1", json={"name": "Eingangsrechnung", "color": "#1565C0"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Eingangsrechnung"
    assert payload["color"] == "#1565C0"


def test_update_document_type_returns_404(client: TestClient) -> None:
    """Updates auf fehlende Dokumenttypen liefern HTTP 404."""
    response = client.patch("/api/document-types/999", json={"name": "Neu"})

    assert response.status_code == 404


def test_delete_document_type(
    client: TestClient, fake_document_type_service: FakeDocumentTypeService
) -> None:
    """Ein Dokumenttyp kann geloescht werden."""
    response = client.delete("/api/document-types/2")

    assert response.status_code == 204
    assert fake_document_type_service.deleted_ids == [2]


def test_delete_document_type_returns_404(client: TestClient) -> None:
    """Loeschen eines fehlenden Dokumenttyps liefert HTTP 404."""
    response = client.delete("/api/document-types/999")

    assert response.status_code == 404

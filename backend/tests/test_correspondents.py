"""Tests fuer Korrespondent-API."""

from fastapi.testclient import TestClient

from tests.conftest import FakeCorrespondentService


def test_list_correspondents(client: TestClient) -> None:
    """Korrespondenten werden als Liste mit Dokumentanzahl geliefert."""
    response = client.get("/api/correspondents")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["name"] == "Stadtwerke"
    assert payload[0]["document_count"] == 1


def test_create_correspondent(client: TestClient) -> None:
    """Ein neuer Korrespondent kann angelegt werden."""
    response = client.post("/api/correspondents", json={"name": "Deutsche Bank"})

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Deutsche Bank"
    assert payload["document_count"] == 0


def test_create_correspondent_returns_existing(client: TestClient) -> None:
    """Ein vorhandener Korrespondent wird zurueckgegeben statt doppelt angelegt."""
    response = client.post("/api/correspondents", json={"name": "Stadtwerke"})

    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_get_correspondent(client: TestClient) -> None:
    """Ein Korrespondent kann per ID geladen werden."""
    response = client.get("/api/correspondents/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Stadtwerke"


def test_get_correspondent_returns_404(client: TestClient) -> None:
    """Fehlende Korrespondenten liefern HTTP 404."""
    response = client.get("/api/correspondents/999")

    assert response.status_code == 404
    assert "Korrespondent mit ID 999" in response.json()["detail"]


def test_update_correspondent(client: TestClient) -> None:
    """Ein Korrespondent kann umbenannt werden."""
    response = client.patch("/api/correspondents/1", json={"name": "Stadtwerke GmbH"})

    assert response.status_code == 200
    assert response.json()["name"] == "Stadtwerke GmbH"


def test_update_correspondent_returns_404(client: TestClient) -> None:
    """Updates auf fehlende Korrespondenten liefern HTTP 404."""
    response = client.patch("/api/correspondents/999", json={"name": "Neu"})

    assert response.status_code == 404


def test_delete_correspondent(
    client: TestClient, fake_correspondent_service: FakeCorrespondentService
) -> None:
    """Ein Korrespondent kann geloescht werden."""
    response = client.delete("/api/correspondents/1")

    assert response.status_code == 204
    assert fake_correspondent_service.deleted_ids == [1]


def test_delete_correspondent_returns_404(client: TestClient) -> None:
    """Loeschen eines fehlenden Korrespondenten liefert HTTP 404."""
    response = client.delete("/api/correspondents/999")

    assert response.status_code == 404

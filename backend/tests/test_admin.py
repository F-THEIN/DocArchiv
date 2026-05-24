"""Tests fuer die Admin-API."""

from fastapi.testclient import TestClient

from tests.conftest import FakeAdminService


def test_get_admin_stats_returns_dashboard_data(client: TestClient) -> None:
    """Der Statistik-Endpunkt liefert fachliche Admin-Kennzahlen."""
    response = client.get("/api/admin/stats")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_documents"] == 2
    assert payload["total_tags"] == 3
    assert payload["documents_by_type"] == {"Rechnung": 1, "Vertrag": 1}
    assert payload["documents_by_month"] == [{"month": "2026-05", "count": 2}]
    assert payload["top_tags"][0] == {"name": "rechnung", "count": 1}
    assert payload["documents_without_tags"] == 1
    assert payload["orphaned_tags"] == 1


def test_get_database_info_returns_technical_data(client: TestClient) -> None:
    """Der Datenbank-Info-Endpunkt liefert technische Metadaten."""
    response = client.get("/api/admin/database-info")

    assert response.status_code == 200
    payload = response.json()
    assert payload["database_size"] == "24 MB"
    assert payload["alembic_revision"] == "001_initial_schema"
    assert payload["postgres_version"] == "PostgreSQL 16.2"
    assert payload["tables"] == [
        {"name": "documents", "row_count": 2, "size": "16 kB"},
        {"name": "tags", "row_count": 3, "size": "16 kB"},
    ]


def test_reset_database_calls_admin_service(client: TestClient, fake_admin_service: FakeAdminService) -> None:
    """Der Reset-Endpunkt loescht Daten ueber den AdminService."""
    response = client.post("/api/admin/reset-database")

    assert response.status_code == 200
    assert fake_admin_service.reset_called is True
    assert response.json() == {
        "message": "Datenbank wurde erfolgreich zurueckgesetzt.",
        "deleted_documents": 2,
        "deleted_tags": 3,
    }

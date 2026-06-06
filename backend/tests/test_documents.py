"""Tests fuer Dokument-API und dokumentbezogene Domain-Schemas."""

from datetime import date

from fastapi.testclient import TestClient
from pydantic import ValidationError

from domain.schemas import DocumentCreate
from domain.services import DocumentService
from tests.conftest import FakeDocumentService


def test_health_endpoint_returns_ok(client: TestClient) -> None:
    """Der Health-Endpunkt liefert Statusinformationen ohne Datenbankzugriff."""
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "DocArchiv",
        "version": "0.1.0",
    }


def test_list_documents_passes_filters_to_service(client: TestClient, fake_document_service: FakeDocumentService) -> None:
    """Dokumentlisten-Query-Parameter werden normalisiert an den Service weitergegeben."""
    response = client.get(
        "/api/documents",
        params={
            "q": " stadtwerke strom ",
            "tags": "Rechnung, haus,",
            "document_type_id": "1",
            "correspondent_id": "1",
            "date_from": "2026-01-01",
            "date_to": "2026-12-31",
            "page": "2",
            "per_page": "10",
            "sort": "relevance",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["page"] == 2
    assert payload["per_page"] == 10
    assert payload["items"][0]["title"] == "Rechnung Stadtwerke Mai 2026"

    assert fake_document_service.last_query is not None
    assert fake_document_service.last_query.q == "stadtwerke strom"
    assert fake_document_service.last_query.tags == ["rechnung", "haus"]
    assert fake_document_service.last_query.document_type_id == 1
    assert fake_document_service.last_query.correspondent_id == 1
    assert fake_document_service.last_query.date_from == date(2026, 1, 1)
    assert fake_document_service.last_query.date_to == date(2026, 12, 31)
    assert fake_document_service.last_query.sort == "relevance"


def test_list_tag_facets_passes_filters_to_service(client: TestClient, fake_document_service: FakeDocumentService) -> None:
    """Tag-Facetten nutzen dieselbe Query-Normalisierung wie die Dokumentliste."""
    response = client.get("/api/documents/tag-facets", params={"tags": "Rechnung, haus,"})

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "rechnung", "color": "#003B7E", "document_count": 1},
        {"id": 2, "name": "haus", "color": None, "document_count": 1},
    ]
    assert fake_document_service.last_query is not None
    assert fake_document_service.last_query.tags == ["rechnung", "haus"]


def test_get_document_returns_document(client: TestClient) -> None:
    """Ein vorhandenes Dokument kann per ID geladen werden."""
    response = client.get("/api/documents/1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert payload["document_type"]["name"] == "Rechnung"
    assert payload["correspondent"]["name"] == "Stadtwerke"
    assert [tag["name"] for tag in payload["tags"]] == ["rechnung", "stadtwerke"]


def test_get_document_returns_404_for_missing_document(client: TestClient) -> None:
    """Fehlende Dokumente werden als HTTP 404 abgebildet."""
    response = client.get("/api/documents/999")

    assert response.status_code == 404
    assert "Dokument mit ID 999" in response.json()["detail"]


def test_create_document_normalizes_tags_and_returns_created_document(client: TestClient) -> None:
    """Die Dokumentanlage validiert Eingaben und normalisiert Tags."""
    response = client.post(
        "/api/documents",
        json={
            "title": " Rechnung Stadtwerke Mai 2026 ",
            "summary": " Rechnung der Stadtwerke fuer Strom und Gas ",
            "original_filename": "scan_001.pdf",
            "stored_filename": "2026-05-20_rechnung-stadtwerke.pdf",
            "document_type_id": 1,
            "correspondent_id": 1,
            "document_date": "2026-05-20",
            "nextcloud_path": "Rechnung/2026-05-20_rechnung-stadtwerke.pdf",
            "tags": ["Rechnung", "stadtwerke", "rechnung", " "],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] == 2
    assert payload["title"] == "Rechnung Stadtwerke Mai 2026"
    assert [tag["name"] for tag in payload["tags"]] == ["rechnung", "stadtwerke"]


def test_create_document_rejects_empty_required_fields(client: TestClient) -> None:
    """Leere Pflichtfelder erzeugen einen Validierungsfehler."""
    response = client.post(
        "/api/documents",
        json={
            "title": "   ",
            "summary": "irrelevant",
            "original_filename": "scan_001.pdf",
            "stored_filename": "scan_001.pdf",
            "document_type_id": 1,
            "nextcloud_path": "Rechnung/scan_001.pdf",
            "tags": [],
        },
    )

    assert response.status_code == 422


def test_update_document_replaces_tags(client: TestClient) -> None:
    """Dokument-Updates koennen Tags ersetzen und Felder aendern."""
    response = client.put(
        "/api/documents/1",
        json={
            "document_type_id": 2,
            "tags": ["Vertrag", "Haus"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["document_type_id"] == 2
    assert [tag["name"] for tag in payload["tags"]] == ["vertrag", "haus"]


def test_update_document_returns_404_for_missing_document(client: TestClient) -> None:
    """Updates auf fehlende Dokumente liefern HTTP 404."""
    response = client.put("/api/documents/999", json={"title": "Neu"})

    assert response.status_code == 404
    assert "Dokument mit ID 999" in response.json()["detail"]


def test_delete_document_removes_document(client: TestClient, fake_document_service: FakeDocumentService) -> None:
    """Ein Dokument kann geloescht werden."""
    response = client.delete("/api/documents/1")

    assert response.status_code == 204
    assert fake_document_service.deleted_document_ids == [1]


def test_delete_document_returns_404_for_missing_document(client: TestClient) -> None:
    """Loeschen eines fehlenden Dokuments liefert HTTP 404."""
    response = client.delete("/api/documents/999")

    assert response.status_code == 404
    assert "Dokument mit ID 999" in response.json()["detail"]


def test_document_create_schema_removes_duplicate_tags() -> None:
    """Das Create-Schema normalisiert Tags deterministisch."""
    schema = DocumentCreate(
        title="Titel",
        summary="Zusammenfassung",
        original_filename="scan.pdf",
        stored_filename="scan.pdf",
        document_type_id=1,
        nextcloud_path="Rechnung/scan.pdf",
        tags=["Rechnung", "rechnung", "Haus", ""],
    )

    assert schema.tags == ["rechnung", "haus"]


def test_document_create_schema_rejects_blank_title() -> None:
    """Das Create-Schema verhindert blanke Pflichtfelder."""
    try:
        DocumentCreate(
            title="  ",
            summary="Zusammenfassung",
            original_filename="scan.pdf",
            stored_filename="scan.pdf",
            document_type_id=1,
            nextcloud_path="Rechnung/scan.pdf",
            tags=[],
        )
    except ValidationError as exc:
        assert "Pflichtfeld darf nicht leer sein" in str(exc)
    else:
        raise AssertionError("ValidationError wurde erwartet.")


def test_document_service_builds_nextcloud_url_for_query_style_base() -> None:
    """Der Nextcloud-URL-Builder behandelt die im Plan definierte dir=-Basis korrekt."""
    service = DocumentService(
        document_repository=object(),
        tag_repository=object(),
        session=object(),
        nextcloud_base_url="https://nextcloud.example.com/apps/files/?dir=/Documents/Scans",
    )

    assert (
        service.build_nextcloud_url("Rechnung/2026-05-20 rechnung.pdf")
        == "https://nextcloud.example.com/apps/files/?dir=/Documents/Scans/Rechnung/2026-05-20%20rechnung.pdf"
    )


def test_document_service_accepts_full_nextcloud_url_unchanged() -> None:
    """Ein kompletter Nextcloud-Link wird direkt als Ziel-URL verwendet."""
    service = DocumentService(
        document_repository=object(),
        tag_repository=object(),
        session=object(),
        nextcloud_base_url="https://nextcloud.example.com/apps/files/?dir=/Documents/Scans",
    )

    full_url = "https://nextcloud.example.com/apps/files/?dir=/Documents/Scans/Rechnung&file=scan_001.pdf"
    normalized_path, resolved_url = service.resolve_nextcloud_reference(full_url)

    assert normalized_path == "Documents/Scans/Rechnung/scan_001.pdf"
    assert resolved_url == full_url


def test_document_service_extracts_path_from_share_url_without_dir_query() -> None:
    """Bei Share-Links ohne dir-Query wird der URL-Pfad als nextcloud_path uebernommen."""
    service = DocumentService(
        document_repository=object(),
        tag_repository=object(),
        session=object(),
        nextcloud_base_url="https://nextcloud.example.com/apps/files/?dir=/Documents/Scans",
    )

    full_url = "https://nextcloud.example.com/s/a1b2c3d4"
    normalized_path, resolved_url = service.resolve_nextcloud_reference(full_url)

    assert normalized_path == "s/a1b2c3d4"
    assert resolved_url == full_url

"""Pytest-Fixtures fuer API-Tests mit FastAPI Dependency-Overrides."""

from collections.abc import Iterator
from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_document_service, get_tag_service
from domain.schemas import (
    DocumentCreate,
    DocumentListResponse,
    DocumentQueryParams,
    DocumentResponse,
    DocumentUpdate,
    PaginatedResponse,
    TagCreate,
    TagResponse,
    TagUpdate,
)
from domain.services import DocumentNotFoundError, TagNotFoundError
from main import app


def utc_datetime() -> datetime:
    """Liefert einen stabilen UTC-Zeitstempel fuer Tests."""
    return datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)


class FakeDocumentService:
    """In-Memory-Ersatz fuer den DocumentService in API-Tests."""

    def __init__(self) -> None:
        """Initialisiert den Fake-Service mit einem Beispieldokument."""
        self.documents: dict[int, DocumentResponse] = {
            1: self._build_document_response(
                document_id=1,
                title="Rechnung Stadtwerke Mai 2026",
                summary="Rechnung der Stadtwerke fuer Strom und Gas",
                document_type="Rechnung",
                tags=["rechnung", "stadtwerke"],
            )
        }
        self.last_query: DocumentQueryParams | None = None
        self.deleted_document_ids: list[int] = []

    def list_documents(self, query: DocumentQueryParams) -> PaginatedResponse[DocumentListResponse]:
        """Liefert eine paginierte Dokumentliste und merkt sich die Query."""
        self.last_query = query
        items = [DocumentListResponse.model_validate(document) for document in self.documents.values()]
        return PaginatedResponse[DocumentListResponse](
            items=items,
            total=len(items),
            page=query.page,
            per_page=query.per_page,
            pages=1 if items else 0,
        )

    def get_document(self, document_id: int) -> DocumentResponse:
        """Liefert ein Dokument oder simuliert einen NotFound-Fehler."""
        document = self.documents.get(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Dokument mit ID {document_id} wurde nicht gefunden.")
        return document

    def create_document(self, data: DocumentCreate) -> DocumentResponse:
        """Erstellt ein Dokument aus validierten Request-Daten."""
        document_id = max(self.documents) + 1
        document = self._build_document_response(
            document_id=document_id,
            title=data.title,
            summary=data.summary,
            document_type=data.document_type,
            tags=data.tags,
            original_filename=data.original_filename,
            stored_filename=data.stored_filename,
            document_date=data.document_date,
            nextcloud_path=data.nextcloud_path,
        )
        self.documents[document_id] = document
        return document

    def update_document(self, document_id: int, data: DocumentUpdate) -> DocumentResponse:
        """Aktualisiert ein Dokument teilweise."""
        existing = self.get_document(document_id)
        update_data = data.model_dump(exclude_unset=True)
        tags = update_data.pop("tags", None)
        updated_payload = existing.model_dump()
        updated_payload.update(update_data)
        if tags is not None:
            updated_payload["tags"] = [TagResponse(id=index + 1, name=tag, color=None, document_count=1) for index, tag in enumerate(tags)]
        updated_payload["updated_at"] = utc_datetime()
        updated = DocumentResponse.model_validate(updated_payload)
        self.documents[document_id] = updated
        return updated

    def delete_document(self, document_id: int) -> None:
        """Loescht ein Dokument oder simuliert einen NotFound-Fehler."""
        self.get_document(document_id)
        del self.documents[document_id]
        self.deleted_document_ids.append(document_id)

    def list_document_types(self) -> list[str]:
        """Liefert die vorhandenen Dokumenttypen."""
        return sorted({document.document_type for document in self.documents.values()})

    def _build_document_response(
        self,
        *,
        document_id: int,
        title: str,
        summary: str,
        document_type: str,
        tags: list[str],
        original_filename: str = "scan_001.pdf",
        stored_filename: str = "2026-05-20_rechnung-stadtwerke.pdf",
        document_date: date | None = date(2026, 5, 20),
        nextcloud_path: str = "Rechnung/2026-05-20_rechnung-stadtwerke.pdf",
    ) -> DocumentResponse:
        """Baut ein konsistentes DocumentResponse-Objekt."""
        return DocumentResponse(
            id=document_id,
            title=title,
            summary=summary,
            original_filename=original_filename,
            stored_filename=stored_filename,
            document_type=document_type,
            document_date=document_date,
            nextcloud_path=nextcloud_path,
            nextcloud_url=f"https://nextcloud.example.com/{nextcloud_path}",
            created_at=utc_datetime(),
            updated_at=utc_datetime(),
            tags=[TagResponse(id=index + 1, name=tag, color=None, document_count=1) for index, tag in enumerate(tags)],
        )


class FakeTagService:
    """In-Memory-Ersatz fuer den TagService in API-Tests."""

    def __init__(self) -> None:
        """Initialisiert den Fake-Service mit Beispiel-Tags."""
        self.tags: dict[int, TagResponse] = {
            1: TagResponse(id=1, name="rechnung", color="#003B7E", document_count=2),
            2: TagResponse(id=2, name="stadtwerke", color=None, document_count=1),
        }
        self.deleted_tag_ids: list[int] = []

    def list_tags(self) -> list[TagResponse]:
        """Liefert alle Tags."""
        return list(self.tags.values())

    def create_tag(self, data: TagCreate) -> TagResponse:
        """Erstellt einen Tag oder liefert den vorhandenen Tag."""
        for tag in self.tags.values():
            if tag.name == data.name:
                return tag
        tag_id = max(self.tags) + 1
        tag = TagResponse(id=tag_id, name=data.name, color=data.color, document_count=0)
        self.tags[tag_id] = tag
        return tag

    def get_tag(self, tag_id: int) -> TagResponse:
        """Liefert einen Tag oder simuliert einen NotFound-Fehler."""
        tag = self.tags.get(tag_id)
        if tag is None:
            raise TagNotFoundError(f"Tag mit ID {tag_id} wurde nicht gefunden.")
        return tag

    def delete_tag(self, tag_id: int) -> None:
        """Loescht einen Tag oder simuliert einen NotFound-Fehler."""
        self.get_tag(tag_id)
        del self.tags[tag_id]
        self.deleted_tag_ids.append(tag_id)

    def update_tag(self, tag_id: int, data: TagUpdate) -> TagResponse:
        """Aktualisiert einen Tag oder simuliert einen NotFound-Fehler."""
        tag = self.get_tag(tag_id)
        update_data = data.model_dump(exclude_unset=True)
        updated = TagResponse(
            id=tag.id,
            name=update_data.get("name", tag.name),
            color=update_data.get("color", tag.color) if "color" in update_data else tag.color,
            document_count=tag.document_count,
        )
        self.tags[tag_id] = updated
        return updated


@pytest.fixture
def fake_document_service() -> FakeDocumentService:
    """Liefert einen frischen FakeDocumentService pro Test."""
    return FakeDocumentService()


@pytest.fixture
def fake_tag_service() -> FakeTagService:
    """Liefert einen frischen FakeTagService pro Test."""
    return FakeTagService()


@pytest.fixture
def client(fake_document_service: FakeDocumentService, fake_tag_service: FakeTagService) -> Iterator[TestClient]:
    """Liefert einen TestClient mit ueberschriebenen Service-Dependencies."""
    app.dependency_overrides[get_document_service] = lambda: fake_document_service
    app.dependency_overrides[get_tag_service] = lambda: fake_tag_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

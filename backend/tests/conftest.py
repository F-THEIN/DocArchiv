"""Pytest-Fixtures fuer API-Tests mit FastAPI Dependency-Overrides."""

from collections.abc import Iterator
from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient

from api.dependencies import (
    get_admin_service,
    get_correspondent_service,
    get_document_service,
    get_document_type_service,
    get_tag_service,
)
from domain.schemas import (
    AdminStatsResponse,
    CorrespondentCount,
    CorrespondentCreate,
    CorrespondentResponse,
    CorrespondentUpdate,
    DatabaseInfoResponse,
    DocumentCreate,
    DocumentListResponse,
    DocumentQueryParams,
    DocumentResponse,
    DocumentTypeCreate,
    DocumentTypeResponse,
    DocumentTypeUpdate,
    DocumentUpdate,
    MonthCount,
    PaginatedResponse,
    ResetDatabaseResponse,
    TableInfo,
    TagCount,
    TagCreate,
    TagResponse,
    TagUpdate,
    TypeCount,
)
from domain.services import (
    CorrespondentNotFoundError,
    DocumentNotFoundError,
    DocumentTypeNotFoundError,
    TagNotFoundError,
)
from main import app


def utc_datetime() -> datetime:
    """Liefert einen stabilen UTC-Zeitstempel fuer Tests."""
    return datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Fake-Dokumenttypen und Korrespondenten fuer Testdaten
# ---------------------------------------------------------------------------

FAKE_DOCUMENT_TYPE_RECHNUNG = DocumentTypeResponse(id=1, name="Rechnung", color="#003B7E", document_count=1)
FAKE_DOCUMENT_TYPE_VERTRAG = DocumentTypeResponse(id=2, name="Vertrag", color="#2E7D32", document_count=0)
FAKE_CORRESPONDENT_STADTWERKE = CorrespondentResponse(id=1, name="Stadtwerke", document_count=1)


# ---------------------------------------------------------------------------
# FakeCorrespondentService
# ---------------------------------------------------------------------------


class FakeCorrespondentService:
    """In-Memory-Ersatz fuer den CorrespondentService in API-Tests."""

    def __init__(self) -> None:
        """Initialisiert den Fake-Service mit Beispiel-Korrespondenten."""
        self.correspondents: dict[int, CorrespondentResponse] = {
            1: CorrespondentResponse(id=1, name="Stadtwerke", document_count=1),
            2: CorrespondentResponse(id=2, name="Allianz", document_count=0),
        }
        self.deleted_ids: list[int] = []

    def list_correspondents(self) -> list[CorrespondentResponse]:
        """Liefert alle Korrespondenten."""
        return list(self.correspondents.values())

    def create_correspondent(self, data: CorrespondentCreate) -> CorrespondentResponse:
        """Erstellt einen Korrespondenten oder liefert den vorhandenen."""
        for c in self.correspondents.values():
            if c.name == data.name:
                return c
        cid = max(self.correspondents) + 1
        c = CorrespondentResponse(id=cid, name=data.name, document_count=0)
        self.correspondents[cid] = c
        return c

    def get_correspondent(self, correspondent_id: int) -> CorrespondentResponse:
        """Liefert einen Korrespondenten oder simuliert NotFound."""
        c = self.correspondents.get(correspondent_id)
        if c is None:
            raise CorrespondentNotFoundError(f"Korrespondent mit ID {correspondent_id} wurde nicht gefunden.")
        return c

    def update_correspondent(self, correspondent_id: int, data: CorrespondentUpdate) -> CorrespondentResponse:
        """Aktualisiert einen Korrespondenten."""
        c = self.get_correspondent(correspondent_id)
        update_data = data.model_dump(exclude_unset=True)
        updated = CorrespondentResponse(
            id=c.id,
            name=update_data.get("name", c.name),
            document_count=c.document_count,
        )
        self.correspondents[correspondent_id] = updated
        return updated

    def delete_correspondent(self, correspondent_id: int) -> None:
        """Loescht einen Korrespondenten."""
        self.get_correspondent(correspondent_id)
        del self.correspondents[correspondent_id]
        self.deleted_ids.append(correspondent_id)


# ---------------------------------------------------------------------------
# FakeDocumentTypeService
# ---------------------------------------------------------------------------


class FakeDocumentTypeService:
    """In-Memory-Ersatz fuer den DocumentTypeService in API-Tests."""

    def __init__(self) -> None:
        """Initialisiert den Fake-Service mit Beispiel-Dokumenttypen."""
        self.document_types: dict[int, DocumentTypeResponse] = {
            1: DocumentTypeResponse(id=1, name="Rechnung", color="#003B7E", document_count=1),
            2: DocumentTypeResponse(id=2, name="Vertrag", color="#2E7D32", document_count=0),
        }
        self.deleted_ids: list[int] = []

    def list_document_types(self) -> list[DocumentTypeResponse]:
        """Liefert alle Dokumenttypen."""
        return list(self.document_types.values())

    def create_document_type(self, data: DocumentTypeCreate) -> DocumentTypeResponse:
        """Erstellt einen Dokumenttyp oder liefert den vorhandenen."""
        for dt in self.document_types.values():
            if dt.name == data.name:
                return dt
        dtid = max(self.document_types) + 1
        dt = DocumentTypeResponse(id=dtid, name=data.name, color=data.color, document_count=0)
        self.document_types[dtid] = dt
        return dt

    def get_document_type(self, document_type_id: int) -> DocumentTypeResponse:
        """Liefert einen Dokumenttyp oder simuliert NotFound."""
        dt = self.document_types.get(document_type_id)
        if dt is None:
            raise DocumentTypeNotFoundError(f"Dokumenttyp mit ID {document_type_id} wurde nicht gefunden.")
        return dt

    def update_document_type(self, document_type_id: int, data: DocumentTypeUpdate) -> DocumentTypeResponse:
        """Aktualisiert einen Dokumenttyp."""
        dt = self.get_document_type(document_type_id)
        update_data = data.model_dump(exclude_unset=True)
        updated = DocumentTypeResponse(
            id=dt.id,
            name=update_data.get("name", dt.name),
            color=update_data.get("color", dt.color) if "color" in update_data else dt.color,
            document_count=dt.document_count,
        )
        self.document_types[document_type_id] = updated
        return updated

    def delete_document_type(self, document_type_id: int) -> None:
        """Loescht einen Dokumenttyp."""
        self.get_document_type(document_type_id)
        del self.document_types[document_type_id]
        self.deleted_ids.append(document_type_id)


# ---------------------------------------------------------------------------
# FakeDocumentService
# ---------------------------------------------------------------------------


class FakeDocumentService:
    """In-Memory-Ersatz fuer den DocumentService in API-Tests."""

    def __init__(self) -> None:
        """Initialisiert den Fake-Service mit einem Beispieldokument."""
        self.documents: dict[int, DocumentResponse] = {
            1: self._build_document_response(
                document_id=1,
                title="Rechnung Stadtwerke Mai 2026",
                summary="Rechnung der Stadtwerke fuer Strom und Gas",
                document_type_id=1,
                document_type=FAKE_DOCUMENT_TYPE_RECHNUNG,
                correspondent_id=1,
                correspondent=FAKE_CORRESPONDENT_STADTWERKE,
                tags=["rechnung", "stadtwerke"],
            )
        }
        self.last_query: DocumentQueryParams | None = None
        self.deleted_document_ids: list[int] = []

    def list_documents(self, query: DocumentQueryParams) -> PaginatedResponse[DocumentListResponse]:
        """Liefert eine paginierte Dokumentliste und merkt sich die Query."""
        self.last_query = query
        items = [DocumentListResponse.model_validate(document.model_dump()) for document in self.documents.values()]
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
            document_type_id=data.document_type_id,
            document_type=FAKE_DOCUMENT_TYPE_RECHNUNG,
            correspondent_id=data.correspondent_id,
            correspondent=FAKE_CORRESPONDENT_STADTWERKE if data.correspondent_id else None,
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
            updated_payload["tags"] = [
                TagResponse(id=index + 1, name=tag, color=None, document_count=1)
                for index, tag in enumerate(tags)
            ]
        updated_payload["updated_at"] = utc_datetime()
        updated = DocumentResponse.model_validate(updated_payload)
        self.documents[document_id] = updated
        return updated

    def delete_document(self, document_id: int) -> None:
        """Loescht ein Dokument oder simuliert einen NotFound-Fehler."""
        self.get_document(document_id)
        del self.documents[document_id]
        self.deleted_document_ids.append(document_id)

    def _build_document_response(
        self,
        *,
        document_id: int,
        title: str,
        summary: str,
        document_type_id: int,
        document_type: DocumentTypeResponse,
        correspondent_id: int | None = None,
        correspondent: CorrespondentResponse | None = None,
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
            document_type_id=document_type_id,
            document_type=document_type,
            correspondent_id=correspondent_id,
            correspondent=correspondent,
            document_date=document_date,
            nextcloud_path=nextcloud_path,
            nextcloud_url=f"https://nextcloud.example.com/{nextcloud_path}",
            created_at=utc_datetime(),
            updated_at=utc_datetime(),
            tags=[TagResponse(id=index + 1, name=tag, color=None, document_count=1) for index, tag in enumerate(tags)],
        )


# ---------------------------------------------------------------------------
# FakeTagService
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# FakeAdminService
# ---------------------------------------------------------------------------


class FakeAdminService:
    """In-Memory-Ersatz fuer den AdminService in API-Tests."""

    def __init__(self) -> None:
        """Initialisiert den Fake-Service mit stabilen Admin-Daten."""
        self.reset_called = False

    def reset_database(self) -> ResetDatabaseResponse:
        """Simuliert das Zuruecksetzen der Datenbank."""
        self.reset_called = True
        return ResetDatabaseResponse(
            message="Datenbank wurde erfolgreich zurueckgesetzt.",
            deleted_documents=2,
            deleted_tags=3,
            deleted_correspondents=1,
            deleted_document_types=2,
        )

    def get_stats(self) -> AdminStatsResponse:
        """Liefert stabile Admin-Statistiken."""
        return AdminStatsResponse(
            total_documents=2,
            total_tags=3,
            total_correspondents=2,
            total_document_types=2,
            documents_by_type=[TypeCount(name="Rechnung", count=1), TypeCount(name="Vertrag", count=1)],
            documents_by_month=[MonthCount(month="2026-05", count=2)],
            top_tags=[TagCount(name="rechnung", count=1), TagCount(name="vertrag", count=1)],
            top_correspondents=[CorrespondentCount(name="Stadtwerke", count=1)],
            documents_without_tags=1,
            documents_without_correspondent=0,
            orphaned_tags=1,
        )

    def get_database_info(self) -> DatabaseInfoResponse:
        """Liefert stabile technische Datenbankinformationen."""
        return DatabaseInfoResponse(
            database_size="24 MB",
            tables=[
                TableInfo(name="correspondents", row_count=2, size="16 kB"),
                TableInfo(name="document_types", row_count=2, size="16 kB"),
                TableInfo(name="documents", row_count=2, size="16 kB"),
                TableInfo(name="tags", row_count=3, size="16 kB"),
            ],
            alembic_revision="001_initial_schema",
            postgres_version="PostgreSQL 16.2",
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_correspondent_service() -> FakeCorrespondentService:
    """Liefert einen frischen FakeCorrespondentService pro Test."""
    return FakeCorrespondentService()


@pytest.fixture
def fake_document_type_service() -> FakeDocumentTypeService:
    """Liefert einen frischen FakeDocumentTypeService pro Test."""
    return FakeDocumentTypeService()


@pytest.fixture
def fake_document_service() -> FakeDocumentService:
    """Liefert einen frischen FakeDocumentService pro Test."""
    return FakeDocumentService()


@pytest.fixture
def fake_tag_service() -> FakeTagService:
    """Liefert einen frischen FakeTagService pro Test."""
    return FakeTagService()


@pytest.fixture
def fake_admin_service() -> FakeAdminService:
    """Liefert einen frischen FakeAdminService pro Test."""
    return FakeAdminService()


@pytest.fixture
def client(
    fake_correspondent_service: FakeCorrespondentService,
    fake_document_type_service: FakeDocumentTypeService,
    fake_document_service: FakeDocumentService,
    fake_tag_service: FakeTagService,
    fake_admin_service: FakeAdminService,
) -> Iterator[TestClient]:
    """Liefert einen TestClient mit ueberschriebenen Service-Dependencies."""
    app.dependency_overrides[get_correspondent_service] = lambda: fake_correspondent_service
    app.dependency_overrides[get_document_type_service] = lambda: fake_document_type_service
    app.dependency_overrides[get_document_service] = lambda: fake_document_service
    app.dependency_overrides[get_tag_service] = lambda: fake_tag_service
    app.dependency_overrides[get_admin_service] = lambda: fake_admin_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

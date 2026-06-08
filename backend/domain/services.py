"""Domain Services fuer Dokumente, Tags, Korrespondenten, Dokumenttypen, Admin-Funktionen und Nextcloud-Linkaufbau."""

import logging
from math import ceil
from typing import Any, Protocol
from urllib.parse import parse_qs, quote, unquote, urlparse

from sqlalchemy import text
from sqlalchemy.orm import Session

from domain.models import Correspondent, Document, DocumentType, Tag
from domain.schemas import (
    AdminStatsResponse,
    CorrespondentCount,
    CorrespondentCreate,
    CorrespondentMerge,
    CorrespondentMergeResponse,
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


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Fehlerklassen
# ---------------------------------------------------------------------------


class DocumentNotFoundError(ValueError):
    """Fehler, wenn ein Dokument nicht gefunden wurde."""


class TagNotFoundError(ValueError):
    """Fehler, wenn ein Tag nicht gefunden wurde."""


class CorrespondentNotFoundError(ValueError):
    """Fehler, wenn ein Korrespondent nicht gefunden wurde."""


class DocumentTypeNotFoundError(ValueError):
    """Fehler, wenn ein Dokumenttyp nicht gefunden wurde."""


# ---------------------------------------------------------------------------
# Repository-Protokolle
# ---------------------------------------------------------------------------


class DocumentRepositoryProtocol(Protocol):
    """Repository-Protokoll fuer Dokumentzugriffe."""

    def get_by_id(self, document_id: int) -> Document | None:
        """Liefert ein Dokument anhand seiner ID."""

    def list_documents(
        self,
        *,
        q: str | None = None,
        tags: list[str] | None = None,
        document_type_id: int | None = None,
        correspondent_id: int | None = None,
        date_from: object | None = None,
        date_to: object | None = None,
        page: int = 1,
        per_page: int = 25,
        sort: str = "date_desc",
    ) -> tuple[list[Document], int]:
        """Liefert gefilterte und paginierte Dokumente."""

    def list_tag_facets(
        self,
        *,
        q: str | None = None,
        tags: list[str] | None = None,
        document_type_id: int | None = None,
        correspondent_id: int | None = None,
        date_from: object | None = None,
        date_to: object | None = None,
    ) -> list[tuple[Tag, int]]:
        """Liefert Tag-Zaehler fuer die aktuelle Dokumentfilterung."""

    def create(self, document: Document) -> Document:
        """Persistiert ein Dokument."""

    def delete(self, document: Document) -> None:
        """Loescht ein Dokument."""


class TagRepositoryProtocol(Protocol):
    """Repository-Protokoll fuer Tagzugriffe."""

    def get_by_id(self, tag_id: int) -> Tag | None:
        """Liefert einen Tag anhand seiner ID."""

    def get_by_name(self, name: str) -> Tag | None:
        """Liefert einen Tag anhand seines Namens."""

    def get_many_by_names(self, names: list[str]) -> list[Tag]:
        """Liefert mehrere Tags anhand ihrer Namen."""

    def get_or_create(self, name: str, color: str | None = None) -> Tag:
        """Liefert einen vorhandenen Tag oder erstellt ihn."""

    def create(self, tag: Tag) -> Tag:
        """Persistiert einen Tag."""

    def list_with_document_counts(self) -> list[tuple[Tag, int]]:
        """Liefert Tags mit Dokumentanzahl."""

    def delete(self, tag: Tag) -> None:
        """Loescht einen Tag."""

    def update(self, tag: Tag) -> Tag:
        """Aktualisiert einen Tag."""


class CorrespondentRepositoryProtocol(Protocol):
    """Repository-Protokoll fuer Korrespondentenzugriffe."""

    def get_by_id(self, correspondent_id: int) -> Correspondent | None:
        """Liefert einen Korrespondenten anhand seiner ID."""

    def get_by_name(self, name: str) -> Correspondent | None:
        """Liefert einen Korrespondenten anhand seines Namens."""

    def get_or_create(self, name: str) -> Correspondent:
        """Liefert einen vorhandenen Korrespondenten oder erstellt ihn."""

    def create(self, correspondent: Correspondent) -> Correspondent:
        """Persistiert einen Korrespondenten."""

    def list_with_document_counts(self) -> list[tuple[Correspondent, int]]:
        """Liefert Korrespondenten mit Dokumentanzahl."""

    def delete(self, correspondent: Correspondent) -> None:
        """Loescht einen Korrespondenten."""

    def update(self, correspondent: Correspondent) -> Correspondent:
        """Aktualisiert einen Korrespondenten."""


class DocumentTypeRepositoryProtocol(Protocol):
    """Repository-Protokoll fuer Dokumenttypzugriffe."""

    def get_by_id(self, document_type_id: int) -> DocumentType | None:
        """Liefert einen Dokumenttyp anhand seiner ID."""

    def get_by_name(self, name: str) -> DocumentType | None:
        """Liefert einen Dokumenttyp anhand seines Namens."""

    def get_or_create(self, name: str, color: str | None = None) -> DocumentType:
        """Liefert einen vorhandenen Dokumenttyp oder erstellt ihn."""

    def create(self, document_type: DocumentType) -> DocumentType:
        """Persistiert einen Dokumenttyp."""

    def list_with_document_counts(self) -> list[tuple[DocumentType, int]]:
        """Liefert Dokumenttypen mit Dokumentanzahl."""

    def delete(self, document_type: DocumentType) -> None:
        """Loescht einen Dokumenttyp."""

    def update(self, document_type: DocumentType) -> DocumentType:
        """Aktualisiert einen Dokumenttyp."""


# ---------------------------------------------------------------------------
# CorrespondentService
# ---------------------------------------------------------------------------


class CorrespondentService:
    """Business-Logik fuer Korrespondenten."""

    def __init__(self, *, correspondent_repository: CorrespondentRepositoryProtocol, session: Session) -> None:
        """Initialisiert den Service mit Repository und Session."""
        self.correspondent_repository = correspondent_repository
        self.session = session

    def list_correspondents(self) -> list[CorrespondentResponse]:
        """Liefert alle Korrespondenten inklusive Dokumentanzahl."""
        correspondents_with_counts = self.correspondent_repository.list_with_document_counts()
        return [
            CorrespondentResponse(
                id=correspondent.id,
                name=correspondent.name,
                document_count=document_count,
            )
            for correspondent, document_count in correspondents_with_counts
        ]

    def create_correspondent(self, data: CorrespondentCreate) -> CorrespondentResponse:
        """Erstellt einen neuen Korrespondenten oder liefert den vorhandenen zurueck."""
        correspondent = self.correspondent_repository.get_or_create(data.name)
        self.session.commit()
        self.session.refresh(correspondent)
        return CorrespondentResponse(
            id=correspondent.id,
            name=correspondent.name,
            document_count=len(correspondent.documents),
        )

    def get_correspondent(self, correspondent_id: int) -> CorrespondentResponse:
        """Liefert einen Korrespondenten anhand seiner ID oder wirft einen NotFound-Fehler."""
        correspondent = self.correspondent_repository.get_by_id(correspondent_id)
        if correspondent is None:
            raise CorrespondentNotFoundError(f"Korrespondent mit ID {correspondent_id} wurde nicht gefunden.")
        return CorrespondentResponse(
            id=correspondent.id,
            name=correspondent.name,
            document_count=len(correspondent.documents),
        )

    def update_correspondent(self, correspondent_id: int, data: CorrespondentUpdate) -> CorrespondentResponse:
        """Aktualisiert einen Korrespondenten oder wirft einen NotFound-Fehler."""
        correspondent = self.correspondent_repository.get_by_id(correspondent_id)
        if correspondent is None:
            raise CorrespondentNotFoundError(f"Korrespondent mit ID {correspondent_id} wurde nicht gefunden.")

        update_data = data.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            setattr(correspondent, field_name, value)

        updated = self.correspondent_repository.update(correspondent)
        self.session.commit()
        return CorrespondentResponse(
            id=updated.id,
            name=updated.name,
            document_count=len(updated.documents),
        )

    def delete_correspondent(self, correspondent_id: int) -> None:
        """Loescht einen Korrespondenten oder wirft einen NotFound-Fehler."""
        correspondent = self.correspondent_repository.get_by_id(correspondent_id)
        if correspondent is None:
            raise CorrespondentNotFoundError(f"Korrespondent mit ID {correspondent_id} wurde nicht gefunden.")
        self.correspondent_repository.delete(correspondent)
        self.session.commit()

    def merge_correspondents(self, data: CorrespondentMerge) -> CorrespondentMergeResponse:
        """Fuehrt mehrere Korrespondenten zu einem Ziel zusammen."""
        target = self.correspondent_repository.get_by_id(data.target_id)
        if target is None:
            raise CorrespondentNotFoundError(f"Ziel-Korrespondent mit ID {data.target_id} wurde nicht gefunden.")

        source_ids = [sid for sid in data.source_ids if sid != data.target_id]
        if not source_ids:
            return CorrespondentMergeResponse(
                target=CorrespondentResponse(id=target.id, name=target.name, document_count=len(target.documents)),
                merged_count=0,
                documents_moved=0,
            )

        documents_moved = 0
        for source_id in source_ids:
            source = self.correspondent_repository.get_by_id(source_id)
            if source is None:
                raise CorrespondentNotFoundError(f"Quell-Korrespondent mit ID {source_id} wurde nicht gefunden.")
            for doc in list(source.documents):
                doc.correspondent_id = target.id
                documents_moved += 1
            self.session.flush()
            self.correspondent_repository.delete(source)

        self.session.commit()
        self.session.refresh(target)
        return CorrespondentMergeResponse(
            target=CorrespondentResponse(id=target.id, name=target.name, document_count=len(target.documents)),
            merged_count=len(source_ids),
            documents_moved=documents_moved,
        )


# ---------------------------------------------------------------------------
# DocumentTypeService
# ---------------------------------------------------------------------------


class DocumentTypeService:
    """Business-Logik fuer Dokumenttypen."""

    def __init__(self, *, document_type_repository: DocumentTypeRepositoryProtocol, session: Session) -> None:
        """Initialisiert den Service mit Repository und Session."""
        self.document_type_repository = document_type_repository
        self.session = session

    def list_document_types(self) -> list[DocumentTypeResponse]:
        """Liefert alle Dokumenttypen inklusive Dokumentanzahl."""
        types_with_counts = self.document_type_repository.list_with_document_counts()
        return [
            DocumentTypeResponse(
                id=dt.id,
                name=dt.name,
                color=dt.color,
                document_count=document_count,
            )
            for dt, document_count in types_with_counts
        ]

    def create_document_type(self, data: DocumentTypeCreate) -> DocumentTypeResponse:
        """Erstellt einen neuen Dokumenttyp oder liefert den vorhandenen zurueck."""
        dt = self.document_type_repository.get_or_create(data.name, data.color)
        self.session.commit()
        self.session.refresh(dt)
        return DocumentTypeResponse(
            id=dt.id,
            name=dt.name,
            color=dt.color,
            document_count=len(dt.documents),
        )

    def get_document_type(self, document_type_id: int) -> DocumentTypeResponse:
        """Liefert einen Dokumenttyp anhand seiner ID oder wirft einen NotFound-Fehler."""
        dt = self.document_type_repository.get_by_id(document_type_id)
        if dt is None:
            raise DocumentTypeNotFoundError(f"Dokumenttyp mit ID {document_type_id} wurde nicht gefunden.")
        return DocumentTypeResponse(
            id=dt.id,
            name=dt.name,
            color=dt.color,
            document_count=len(dt.documents),
        )

    def update_document_type(self, document_type_id: int, data: DocumentTypeUpdate) -> DocumentTypeResponse:
        """Aktualisiert einen Dokumenttyp oder wirft einen NotFound-Fehler."""
        dt = self.document_type_repository.get_by_id(document_type_id)
        if dt is None:
            raise DocumentTypeNotFoundError(f"Dokumenttyp mit ID {document_type_id} wurde nicht gefunden.")

        update_data = data.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            setattr(dt, field_name, value)

        updated = self.document_type_repository.update(dt)
        self.session.commit()
        return DocumentTypeResponse(
            id=updated.id,
            name=updated.name,
            color=updated.color,
            document_count=len(updated.documents),
        )

    def delete_document_type(self, document_type_id: int) -> None:
        """Loescht einen Dokumenttyp oder wirft einen NotFound-Fehler."""
        dt = self.document_type_repository.get_by_id(document_type_id)
        if dt is None:
            raise DocumentTypeNotFoundError(f"Dokumenttyp mit ID {document_type_id} wurde nicht gefunden.")
        self.document_type_repository.delete(dt)
        self.session.commit()


# ---------------------------------------------------------------------------
# DocumentService
# ---------------------------------------------------------------------------


class DocumentService:
    """Business-Logik fuer Dokumente."""

    def __init__(
        self,
        *,
        document_repository: DocumentRepositoryProtocol,
        tag_repository: TagRepositoryProtocol,
        session: Session,
        nextcloud_base_url: str,
    ) -> None:
        """Initialisiert den Service mit Repositories und Konfiguration."""
        self.document_repository = document_repository
        self.tag_repository = tag_repository
        self.session = session
        self.nextcloud_base_url = nextcloud_base_url

    def list_documents(self, query: DocumentQueryParams) -> PaginatedResponse[DocumentListResponse]:
        """Liefert Dokumente als paginierte Response."""
        documents, total = self.document_repository.list_documents(
            q=query.q,
            tags=query.tags,
            document_type_id=query.document_type_id,
            correspondent_id=query.correspondent_id,
            date_from=query.date_from,
            date_to=query.date_to,
            page=query.page,
            per_page=query.per_page,
            sort=query.sort,
        )
        pages = ceil(total / query.per_page) if total else 0
        return PaginatedResponse[DocumentListResponse](
            items=[DocumentListResponse.model_validate(document) for document in documents],
            total=total,
            page=query.page,
            per_page=query.per_page,
            pages=pages,
        )

    def list_tag_facets(self, query: DocumentQueryParams) -> list[TagResponse]:
        """Liefert Tag-Zaehler passend zur aktuellen Dokumentfilterung."""
        tags_with_counts = self.document_repository.list_tag_facets(
            q=query.q,
            tags=query.tags,
            document_type_id=query.document_type_id,
            correspondent_id=query.correspondent_id,
            date_from=query.date_from,
            date_to=query.date_to,
        )
        return [
            TagResponse(
                id=tag.id,
                name=tag.name,
                color=tag.color,
                document_count=document_count,
            )
            for tag, document_count in tags_with_counts
        ]

    def get_document(self, document_id: int) -> DocumentResponse:
        """Liefert ein einzelnes Dokument oder wirft einen NotFound-Fehler."""
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Dokument mit ID {document_id} wurde nicht gefunden.")
        return DocumentResponse.model_validate(document)

    def create_document(self, data: DocumentCreate) -> DocumentResponse:
        """Erstellt ein Dokument inklusive Tags und Nextcloud-URL."""
        normalized_nextcloud_path, resolved_nextcloud_url = self.resolve_nextcloud_reference(data.nextcloud_path)
        document = Document(
            title=data.title,
            summary=data.summary,
            original_filename=data.original_filename,
            stored_filename=data.stored_filename,
            document_type_id=data.document_type_id,
            correspondent_id=data.correspondent_id,
            document_date=data.document_date,
            nextcloud_path=normalized_nextcloud_path,
            nextcloud_url=resolved_nextcloud_url,
        )
        document.tags = self._get_or_create_tags(data.tags)

        created_document = self.document_repository.create(document)
        self.session.commit()
        self.session.refresh(created_document)
        return DocumentResponse.model_validate(created_document)

    def update_document(self, document_id: int, data: DocumentUpdate) -> DocumentResponse:
        """Aktualisiert ein Dokument teilweise und ersetzt Tags bei Bedarf."""
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Dokument mit ID {document_id} wurde nicht gefunden.")

        update_data = data.model_dump(exclude_unset=True)
        tags = update_data.pop("tags", None)

        for field_name, value in update_data.items():
            if field_name == "nextcloud_path":
                normalized_nextcloud_path, resolved_nextcloud_url = self.resolve_nextcloud_reference(str(value))
                document.nextcloud_path = normalized_nextcloud_path
                document.nextcloud_url = resolved_nextcloud_url
                continue
            setattr(document, field_name, value)

        if tags is not None:
            document.tags = self._get_or_create_tags(tags)

        self.session.flush()
        self.session.commit()
        self.session.refresh(document)
        return DocumentResponse.model_validate(document)

    def delete_document(self, document_id: int) -> None:
        """Loescht ein Dokument oder wirft einen NotFound-Fehler."""
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Dokument mit ID {document_id} wurde nicht gefunden.")
        self.document_repository.delete(document)
        self.session.commit()

    def build_nextcloud_url(self, nextcloud_path: str) -> str:
        """Baut einen Nextcloud-Link aus Basis-URL und relativem Dokumentpfad."""
        if self._is_absolute_http_url(nextcloud_path):
            return nextcloud_path.strip()

        normalized_base_url = self.nextcloud_base_url.rstrip("/")
        normalized_path = nextcloud_path.strip().lstrip("/")
        encoded_path = quote(normalized_path, safe="/")

        separator = "" if normalized_base_url.endswith("=") else "/"
        return f"{normalized_base_url}{separator}{encoded_path}"

    def resolve_nextcloud_reference(self, nextcloud_reference: str) -> tuple[str, str]:
        """Normalisiert Nextcloud-Referenz und liefert Pfad plus aufrufbare URL."""
        normalized_reference = nextcloud_reference.strip()

        if self._is_absolute_http_url(normalized_reference):
            return self._extract_nextcloud_path_from_url(normalized_reference), normalized_reference

        normalized_path = normalized_reference.lstrip("/")
        return normalized_path, self.build_nextcloud_url(normalized_path)

    @staticmethod
    def _is_absolute_http_url(value: str) -> bool:
        """Prueft, ob ein Wert eine absolute HTTP- oder HTTPS-URL ist."""
        parsed_url = urlparse(value)
        return parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)

    @staticmethod
    def _extract_nextcloud_path_from_url(nextcloud_url: str) -> str:
        """Leitet einen darstellbaren Nextcloud-Pfad aus einer URL ab."""
        parsed_url = urlparse(nextcloud_url)
        query_params = parse_qs(parsed_url.query)

        nextcloud_dir = unquote(query_params.get("dir", [""])[0]).strip()
        nextcloud_file = unquote(query_params.get("file", [""])[0]).strip()

        if nextcloud_dir:
            normalized_dir = nextcloud_dir.lstrip("/").rstrip("/")
            normalized_file = nextcloud_file.lstrip("/")
            if normalized_file:
                return f"{normalized_dir}/{normalized_file}"
            return normalized_dir

        path_from_url = unquote(parsed_url.path).strip().lstrip("/")
        return path_from_url or nextcloud_url.strip()

    def _get_or_create_tags(self, tag_names: list[str]) -> list[Tag]:
        """Liefert Tag-Modelle fuer normalisierte Namen und erstellt fehlende Tags."""
        tags: list[Tag] = []
        for tag_name in tag_names:
            normalized_name = tag_name.strip().lower()
            if normalized_name:
                tags.append(self.tag_repository.get_or_create(normalized_name))
        return tags


# ---------------------------------------------------------------------------
# TagService
# ---------------------------------------------------------------------------


class TagService:
    """Business-Logik fuer Tags."""

    def __init__(self, *, tag_repository: TagRepositoryProtocol, session: Session) -> None:
        """Initialisiert den Service mit Repository und Session."""
        self.tag_repository = tag_repository
        self.session = session

    def list_tags(self) -> list[TagResponse]:
        """Liefert alle Tags inklusive Dokumentanzahl."""
        tags_with_counts = self.tag_repository.list_with_document_counts()
        return [
            TagResponse(
                id=tag.id,
                name=tag.name,
                color=tag.color,
                document_count=document_count,
            )
            for tag, document_count in tags_with_counts
        ]

    def create_tag(self, data: TagCreate) -> TagResponse:
        """Erstellt einen neuen Tag oder liefert den vorhandenen Tag zurueck."""
        tag = self.tag_repository.get_or_create(data.name, data.color)
        self.session.commit()
        self.session.refresh(tag)
        return TagResponse(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            document_count=len(tag.documents),
        )

    def get_tag(self, tag_id: int) -> TagResponse:
        """Liefert einen Tag anhand seiner ID oder wirft einen NotFound-Fehler."""
        tag = self.tag_repository.get_by_id(tag_id)
        if tag is None:
            raise TagNotFoundError(f"Tag mit ID {tag_id} wurde nicht gefunden.")
        return TagResponse(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            document_count=len(tag.documents),
        )

    def delete_tag(self, tag_id: int) -> None:
        """Loescht einen Tag oder wirft einen NotFound-Fehler."""
        tag = self.tag_repository.get_by_id(tag_id)
        if tag is None:
            raise TagNotFoundError(f"Tag mit ID {tag_id} wurde nicht gefunden.")
        self.tag_repository.delete(tag)
        self.session.commit()

    def update_tag(self, tag_id: int, data: TagUpdate) -> TagResponse:
        """Aktualisiert einen Tag oder wirft einen NotFound-Fehler."""
        tag = self.tag_repository.get_by_id(tag_id)
        if tag is None:
            raise TagNotFoundError(f"Tag mit ID {tag_id} wurde nicht gefunden.")

        update_data = data.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            setattr(tag, field_name, value)

        updated_tag = self.tag_repository.update(tag)
        self.session.commit()
        return TagResponse(
            id=updated_tag.id,
            name=updated_tag.name,
            color=updated_tag.color,
            document_count=len(updated_tag.documents),
        )


# ---------------------------------------------------------------------------
# AdminService
# ---------------------------------------------------------------------------


class AdminService:
    """Business-Logik fuer administrative Funktionen."""

    def __init__(self, *, session: Session) -> None:
        """Initialisiert den Service mit einer Datenbank-Session."""
        self.session = session

    def reset_database(self) -> ResetDatabaseResponse:
        """Loescht alle Dokument-, Tag-, Korrespondent- und Dokumenttyp-Daten unwiderruflich."""
        deleted_documents = self._count_table_rows("documents")
        deleted_tags = self._count_table_rows("tags")
        deleted_correspondents = self._count_table_rows("correspondents")
        deleted_document_types = self._count_table_rows("document_types")

        logger.warning(
            "Admin-Aktion: Datenbank wird zurueckgesetzt. Dokumente=%s Tags=%s Korrespondenten=%s Dokumenttypen=%s",
            deleted_documents,
            deleted_tags,
            deleted_correspondents,
            deleted_document_types,
        )
        self.session.execute(
            text("TRUNCATE TABLE document_tags, documents, tags, correspondents, document_types RESTART IDENTITY CASCADE")
        )
        self.session.commit()

        return ResetDatabaseResponse(
            message="Datenbank wurde erfolgreich zurueckgesetzt.",
            deleted_documents=deleted_documents,
            deleted_tags=deleted_tags,
            deleted_correspondents=deleted_correspondents,
            deleted_document_types=deleted_document_types,
        )

    def get_stats(self) -> AdminStatsResponse:
        """Liefert fachliche Statistiken fuer die Admin-Seite."""
        total_documents = self._count_table_rows("documents")
        total_tags = self._count_table_rows("tags")
        total_correspondents = self._count_table_rows("correspondents")
        total_document_types = self._count_table_rows("document_types")

        documents_by_type = [
            TypeCount(name=str(row._mapping["name"]), count=int(row._mapping["count"]))
            for row in self.session.execute(
                text(
                    """
                    SELECT dt.name AS name, COUNT(d.id) AS count
                    FROM document_types dt
                    LEFT JOIN documents d ON d.document_type_id = dt.id
                    GROUP BY dt.id, dt.name
                    ORDER BY count DESC, dt.name ASC
                    """
                )
            )
        ]

        documents_by_month = [
            MonthCount(month=str(row._mapping["month"]), count=int(row._mapping["count"]))
            for row in self.session.execute(
                text(
                    """
                    SELECT to_char(date_trunc('month', COALESCE(document_date, created_at::date)), 'YYYY-MM') AS month,
                           COUNT(*) AS count
                    FROM documents
                    GROUP BY month
                    ORDER BY month DESC
                    LIMIT 12
                    """
                )
            )
        ]
        documents_by_month.reverse()

        top_tags = [
            TagCount(name=str(row._mapping["name"]), count=int(row._mapping["count"]))
            for row in self.session.execute(
                text(
                    """
                    SELECT tags.name AS name, COUNT(document_tags.document_id) AS count
                    FROM tags
                    LEFT JOIN document_tags ON document_tags.tag_id = tags.id
                    GROUP BY tags.id, tags.name
                    ORDER BY count DESC, tags.name ASC
                    LIMIT 10
                    """
                )
            )
        ]

        top_correspondents = [
            CorrespondentCount(name=str(row._mapping["name"]), count=int(row._mapping["count"]))
            for row in self.session.execute(
                text(
                    """
                    SELECT c.name AS name, COUNT(d.id) AS count
                    FROM correspondents c
                    LEFT JOIN documents d ON d.correspondent_id = c.id
                    GROUP BY c.id, c.name
                    ORDER BY count DESC, c.name ASC
                    LIMIT 10
                    """
                )
            )
        ]

        documents_without_tags = int(
            self.session.scalar(
                text(
                    """
                    SELECT COUNT(*)
                    FROM documents
                    WHERE NOT EXISTS (
                        SELECT 1 FROM document_tags WHERE document_tags.document_id = documents.id
                    )
                    """
                )
            )
            or 0
        )

        documents_without_correspondent = int(
            self.session.scalar(
                text(
                    """
                    SELECT COUNT(*)
                    FROM documents
                    WHERE correspondent_id IS NULL
                    """
                )
            )
            or 0
        )

        orphaned_tags = int(
            self.session.scalar(
                text(
                    """
                    SELECT COUNT(*)
                    FROM tags
                    WHERE NOT EXISTS (
                        SELECT 1 FROM document_tags WHERE document_tags.tag_id = tags.id
                    )
                    """
                )
            )
            or 0
        )

        return AdminStatsResponse(
            total_documents=total_documents,
            total_tags=total_tags,
            total_correspondents=total_correspondents,
            total_document_types=total_document_types,
            documents_by_type=documents_by_type,
            documents_by_month=documents_by_month,
            top_tags=top_tags,
            top_correspondents=top_correspondents,
            documents_without_tags=documents_without_tags,
            documents_without_correspondent=documents_without_correspondent,
            orphaned_tags=orphaned_tags,
        )

    def get_database_info(self) -> DatabaseInfoResponse:
        """Liefert technische Informationen zur PostgreSQL-Datenbank."""
        database_size = str(
            self.session.scalar(text("SELECT pg_size_pretty(pg_database_size(current_database()))")) or "unbekannt"
        )
        postgres_version = str(self.session.scalar(text("SELECT version()")) or "unbekannt")
        alembic_revision = self._get_alembic_revision()
        tables = [
            TableInfo(
                name=str(row._mapping["name"]),
                row_count=int(row._mapping["row_count"]),
                size=str(row._mapping["size"]),
            )
            for row in self.session.execute(
                text(
                    """
                    SELECT relname AS name,
                           n_live_tup::bigint AS row_count,
                           pg_size_pretty(pg_total_relation_size(relid)) AS size
                    FROM pg_stat_user_tables
                    WHERE schemaname = 'public'
                    ORDER BY relname ASC
                    """
                )
            )
        ]

        return DatabaseInfoResponse(
            database_size=database_size,
            tables=tables,
            alembic_revision=alembic_revision,
            postgres_version=postgres_version,
        )

    def _count_table_rows(self, table_name: str) -> int:
        """Zaehlt Zeilen einer bekannten Anwendungstabelle."""
        allowed_tables = {"documents", "tags", "document_tags", "correspondents", "document_types"}
        if table_name not in allowed_tables:
            raise ValueError(f"Unbekannte Tabelle: {table_name}")
        return int(self.session.scalar(text(f"SELECT COUNT(*) FROM {table_name}")) or 0)

    def _get_alembic_revision(self) -> str | None:
        """Liest die aktuelle Alembic-Revision, falls die Versionstabelle existiert."""
        table_exists = bool(
            self.session.scalar(
                text(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = 'public' AND table_name = 'alembic_version'
                    )
                    """
                )
            )
        )
        if not table_exists:
            return None
        revision: Any = self.session.scalar(text("SELECT version_num FROM alembic_version LIMIT 1"))
        return str(revision) if revision is not None else None

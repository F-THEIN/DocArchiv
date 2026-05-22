"""Domain Services fuer Dokumente, Tags und Nextcloud-Linkaufbau."""

from math import ceil
from typing import Protocol
from urllib.parse import quote

from sqlalchemy.orm import Session

from domain.models import Document, Tag
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


class DocumentNotFoundError(ValueError):
    """Fehler, wenn ein Dokument nicht gefunden wurde."""


class TagNotFoundError(ValueError):
    """Fehler, wenn ein Tag nicht gefunden wurde."""


class DocumentRepositoryProtocol(Protocol):
    """Repository-Protokoll fuer Dokumentzugriffe."""

    def get_by_id(self, document_id: int) -> Document | None:
        """Liefert ein Dokument anhand seiner ID."""

    def list_documents(
        self,
        *,
        q: str | None = None,
        tags: list[str] | None = None,
        document_type: str | None = None,
        date_from: object | None = None,
        date_to: object | None = None,
        page: int = 1,
        per_page: int = 25,
        sort: str = "date_desc",
    ) -> tuple[list[Document], int]:
        """Liefert gefilterte und paginierte Dokumente."""

    def create(self, document: Document) -> Document:
        """Persistiert ein Dokument."""

    def delete(self, document: Document) -> None:
        """Loescht ein Dokument."""

    def list_document_types(self) -> list[str]:
        """Liefert alle Dokumenttypen."""


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
            document_type=query.document_type,
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

    def get_document(self, document_id: int) -> DocumentResponse:
        """Liefert ein einzelnes Dokument oder wirft einen NotFound-Fehler."""
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(f"Dokument mit ID {document_id} wurde nicht gefunden.")
        return DocumentResponse.model_validate(document)

    def create_document(self, data: DocumentCreate) -> DocumentResponse:
        """Erstellt ein Dokument inklusive Tags und Nextcloud-URL."""
        document = Document(
            title=data.title,
            summary=data.summary,
            original_filename=data.original_filename,
            stored_filename=data.stored_filename,
            document_type=data.document_type,
            document_date=data.document_date,
            nextcloud_path=data.nextcloud_path,
            nextcloud_url=self.build_nextcloud_url(data.nextcloud_path),
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
            setattr(document, field_name, value)

        if "nextcloud_path" in update_data:
            document.nextcloud_url = self.build_nextcloud_url(document.nextcloud_path)

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

    def list_document_types(self) -> list[str]:
        """Liefert alle bekannten Dokumenttypen."""
        return self.document_repository.list_document_types()

    def build_nextcloud_url(self, nextcloud_path: str) -> str:
        """Baut einen Nextcloud-Link aus Basis-URL und relativem Dokumentpfad."""
        normalized_base_url = self.nextcloud_base_url.rstrip("/")
        normalized_path = nextcloud_path.strip().lstrip("/")
        encoded_path = quote(normalized_path, safe="/")

        separator = "" if normalized_base_url.endswith("=") else "/"
        return f"{normalized_base_url}{separator}{encoded_path}"

    def _get_or_create_tags(self, tag_names: list[str]) -> list[Tag]:
        """Liefert Tag-Modelle fuer normalisierte Namen und erstellt fehlende Tags."""
        tags: list[Tag] = []
        for tag_name in tag_names:
            normalized_name = tag_name.strip().lower()
            if normalized_name:
                tags.append(self.tag_repository.get_or_create(normalized_name))
        return tags


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

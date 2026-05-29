"""Pydantic-Schemas fuer Requests und Responses der DocArchiv-Domain."""

from datetime import date, datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator


T = TypeVar("T")


# ---------------------------------------------------------------------------
# Korrespondent
# ---------------------------------------------------------------------------


class CorrespondentBase(BaseModel):
    """Gemeinsame Felder fuer Korrespondent-Schemas."""

    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """Normalisiert Korrespondent-Namen ohne umgebende Leerzeichen."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("Korrespondent-Name darf nicht leer sein.")
        return normalized


class CorrespondentCreate(CorrespondentBase):
    """Request-Schema zum Anlegen eines Korrespondenten."""


class CorrespondentUpdate(BaseModel):
    """Request-Schema fuer teilweise Korrespondent-Updates."""

    name: str | None = Field(default=None, min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        """Normalisiert optionalen Korrespondent-Namen."""
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Korrespondent-Name darf nicht leer sein.")
        return normalized


class CorrespondentResponse(CorrespondentBase):
    """Response-Schema fuer Korrespondenten."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    document_count: int = 0


# ---------------------------------------------------------------------------
# Dokumenttyp
# ---------------------------------------------------------------------------


class DocumentTypeBase(BaseModel):
    """Gemeinsame Felder fuer Dokumenttyp-Schemas."""

    name: str = Field(min_length=1, max_length=100)
    color: str | None = Field(default=None, max_length=32)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """Normalisiert Dokumenttyp-Namen ohne umgebende Leerzeichen."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("Dokumenttyp-Name darf nicht leer sein.")
        return normalized

    @field_validator("color")
    @classmethod
    def normalize_color(cls, value: str | None) -> str | None:
        """Normalisiert optionale Farbwerte."""
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class DocumentTypeCreate(DocumentTypeBase):
    """Request-Schema zum Anlegen eines Dokumenttyps."""


class DocumentTypeUpdate(BaseModel):
    """Request-Schema fuer teilweise Dokumenttyp-Updates."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, max_length=32)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        """Normalisiert optionalen Dokumenttyp-Namen."""
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Dokumenttyp-Name darf nicht leer sein.")
        return normalized

    @field_validator("color")
    @classmethod
    def normalize_color(cls, value: str | None) -> str | None:
        """Normalisiert optionalen Farbwert."""
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class DocumentTypeResponse(DocumentTypeBase):
    """Response-Schema fuer Dokumenttypen."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    document_count: int = 0


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------


class TagBase(BaseModel):
    """Gemeinsame Felder fuer Tag-Schemas."""

    name: str = Field(min_length=1, max_length=80)
    color: str | None = Field(default=None, max_length=32)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """Normalisiert Tag-Namen auf lowercase ohne umgebende Leerzeichen."""
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("Tag-Name darf nicht leer sein.")
        return normalized

    @field_validator("color")
    @classmethod
    def normalize_color(cls, value: str | None) -> str | None:
        """Normalisiert optionale Farbwerte."""
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class TagCreate(TagBase):
    """Request-Schema zum Anlegen eines Tags."""


class TagUpdate(BaseModel):
    """Request-Schema fuer teilweise Tag-Updates."""

    name: str | None = Field(default=None, min_length=1, max_length=80)
    color: str | None = Field(default=None, max_length=32)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        """Normalisiert optionalen Tag-Namen auf lowercase ohne umgebende Leerzeichen."""
        if value is None:
            return None
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("Tag-Name darf nicht leer sein.")
        return normalized

    @field_validator("color")
    @classmethod
    def normalize_color(cls, value: str | None) -> str | None:
        """Normalisiert optionalen Farbwert."""
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class TagResponse(TagBase):
    """Response-Schema fuer Tags."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    document_count: int = 0


# ---------------------------------------------------------------------------
# Dokument
# ---------------------------------------------------------------------------


class DocumentBase(BaseModel):
    """Gemeinsame Dokumentfelder fuer Create-, Update- und Response-Schemas."""

    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(default="")
    original_filename: str = Field(min_length=1, max_length=255)
    stored_filename: str = Field(min_length=1, max_length=255)
    document_type_id: int | None = Field(default=None, gt=0)
    correspondent_id: int | None = Field(default=None, gt=0)
    document_date: date | None = None
    nextcloud_path: str = Field(min_length=1, max_length=1024)

    @field_validator("title", "original_filename", "stored_filename", "nextcloud_path")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        """Entfernt Whitespace und verhindert leere Pflichtfelder."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("Pflichtfeld darf nicht leer sein.")
        return normalized

    @field_validator("summary")
    @classmethod
    def strip_summary(cls, value: str) -> str:
        """Normalisiert die Zusammenfassung."""
        return value.strip()


class DocumentCreate(DocumentBase):
    """Request-Schema zum Anlegen eines Dokuments durch die Scan-Pipeline."""

    tags: list[str] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: list[str]) -> list[str]:
        """Normalisiert Tag-Liste, entfernt Duplikate und ignoriert leere Eintraege."""
        normalized_tags: list[str] = []
        seen: set[str] = set()
        for tag in value:
            normalized = tag.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                normalized_tags.append(normalized)
        return normalized_tags


class DocumentUpdate(BaseModel):
    """Request-Schema fuer teilweise Dokument-Updates aus der SPA."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = None
    original_filename: str | None = Field(default=None, min_length=1, max_length=255)
    stored_filename: str | None = Field(default=None, min_length=1, max_length=255)
    document_type_id: int | None = Field(default=None, gt=0)
    correspondent_id: int | None = Field(default=None, gt=0)
    document_date: date | None = None
    nextcloud_path: str | None = Field(default=None, min_length=1, max_length=1024)
    tags: list[str] | None = None

    @field_validator("title", "original_filename", "stored_filename", "nextcloud_path")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        """Normalisiert optionale Textfelder."""
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Feld darf nicht leer sein.")
        return normalized

    @field_validator("summary")
    @classmethod
    def strip_optional_summary(cls, value: str | None) -> str | None:
        """Normalisiert eine optionale Zusammenfassung."""
        if value is None:
            return None
        return value.strip()

    @field_validator("tags")
    @classmethod
    def normalize_optional_tags(cls, value: list[str] | None) -> list[str] | None:
        """Normalisiert optionale Tags fuer Updates."""
        if value is None:
            return None
        normalized_tags: list[str] = []
        seen: set[str] = set()
        for tag in value:
            normalized = tag.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                normalized_tags.append(normalized)
        return normalized_tags


class DocumentResponse(DocumentBase):
    """Response-Schema fuer ein Dokument."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    nextcloud_url: str
    created_at: datetime
    updated_at: datetime
    document_type: DocumentTypeResponse | None = Field(default=None, validation_alias="document_type_rel")
    correspondent: CorrespondentResponse | None = None
    tags: list[TagResponse] = Field(default_factory=list)


class DocumentListResponse(BaseModel):
    """Reduziertes Response-Schema fuer Dokumentlisten."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str
    summary: str
    original_filename: str
    stored_filename: str
    document_type_id: int | None
    correspondent_id: int | None
    document_date: date | None
    nextcloud_path: str
    nextcloud_url: str
    created_at: datetime
    updated_at: datetime
    document_type: DocumentTypeResponse | None = Field(default=None, validation_alias="document_type_rel")
    correspondent: CorrespondentResponse | None = None
    tags: list[TagResponse] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Pagination & Query
# ---------------------------------------------------------------------------


class PaginatedResponse(BaseModel, Generic[T]):
    """Generisches Schema fuer paginierte API-Antworten."""

    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    per_page: int = Field(ge=1)
    pages: int = Field(ge=0)


class DocumentQueryParams(BaseModel):
    """Validierte Query-Parameter fuer die Dokumentensuche."""

    q: str | None = None
    tags: list[str] = Field(default_factory=list)
    document_type_id: int | None = None
    correspondent_id: int | None = None
    date_from: date | None = None
    date_to: date | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)
    sort: str = Field(default="date_desc")

    @field_validator("q")
    @classmethod
    def strip_optional_query_text(cls, value: str | None) -> str | None:
        """Normalisiert optionale Query-Textwerte."""
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("tags")
    @classmethod
    def normalize_query_tags(cls, value: list[str]) -> list[str]:
        """Normalisiert Query-Tags."""
        return [tag.strip().lower() for tag in value if tag.strip()]


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------


class MonthCount(BaseModel):
    """Statistikwert fuer Dokumente pro Monat."""

    month: str
    count: int = Field(ge=0)


class TagCount(BaseModel):
    """Statistikwert fuer Tags mit Dokumentanzahl."""

    name: str
    count: int = Field(ge=0)


class TypeCount(BaseModel):
    """Statistikwert fuer Dokumenttypen mit Dokumentanzahl."""

    name: str
    count: int = Field(ge=0)


class CorrespondentCount(BaseModel):
    """Statistikwert fuer Korrespondenten mit Dokumentanzahl."""

    name: str
    count: int = Field(ge=0)


class AdminStatsResponse(BaseModel):
    """Response-Schema fuer Admin-Statistiken."""

    total_documents: int = Field(ge=0)
    total_tags: int = Field(ge=0)
    total_correspondents: int = Field(ge=0)
    total_document_types: int = Field(ge=0)
    documents_by_type: list[TypeCount]
    documents_by_month: list[MonthCount]
    top_tags: list[TagCount]
    top_correspondents: list[CorrespondentCount]
    documents_without_tags: int = Field(ge=0)
    documents_without_correspondent: int = Field(ge=0)
    orphaned_tags: int = Field(ge=0)


class TableInfo(BaseModel):
    """Technische Informationen zu einer Datenbanktabelle."""

    name: str
    row_count: int = Field(ge=0)
    size: str


class DatabaseInfoResponse(BaseModel):
    """Response-Schema fuer technische Datenbankinformationen."""

    database_size: str
    tables: list[TableInfo]
    alembic_revision: str | None
    postgres_version: str


class ResetDatabaseResponse(BaseModel):
    """Response-Schema fuer das Zuruecksetzen der Datenbank."""

    message: str
    deleted_documents: int = Field(ge=0)
    deleted_tags: int = Field(ge=0)
    deleted_correspondents: int = Field(ge=0)
    deleted_document_types: int = Field(ge=0)

"""Pydantic-Schemas fuer Requests und Responses der DocArchiv-Domain."""

from datetime import date, datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator


T = TypeVar("T")


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


class DocumentBase(BaseModel):
    """Gemeinsame Dokumentfelder fuer Create-, Update- und Response-Schemas."""

    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(default="")
    original_filename: str = Field(min_length=1, max_length=255)
    stored_filename: str = Field(min_length=1, max_length=255)
    document_type: str = Field(min_length=1, max_length=100)
    document_date: date | None = None
    nextcloud_path: str = Field(min_length=1, max_length=1024)

    @field_validator("title", "original_filename", "stored_filename", "document_type", "nextcloud_path")
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
    document_type: str | None = Field(default=None, min_length=1, max_length=100)
    document_date: date | None = None
    nextcloud_path: str | None = Field(default=None, min_length=1, max_length=1024)
    tags: list[str] | None = None

    @field_validator("title", "original_filename", "stored_filename", "document_type", "nextcloud_path")
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

    model_config = ConfigDict(from_attributes=True)

    id: int
    nextcloud_url: str
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = Field(default_factory=list)


class DocumentListResponse(BaseModel):
    """Reduziertes Response-Schema fuer Dokumentlisten."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str
    original_filename: str
    stored_filename: str
    document_type: str
    document_date: date | None
    nextcloud_path: str
    nextcloud_url: str
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = Field(default_factory=list)


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
    document_type: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)
    sort: str = Field(default="date_desc")

    @field_validator("q", "document_type")
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

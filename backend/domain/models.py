"""SQLAlchemy-Domain-Models fuer Dokumente und Tags."""

from datetime import date, datetime
from typing import List

from sqlalchemy import Computed, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Gemeinsame deklarative SQLAlchemy-Basis fuer alle ORM-Models."""


class DocumentTag(Base):
    """Association-Model fuer die M:N-Beziehung zwischen Dokumenten und Tags."""

    __tablename__ = "document_tags"
    __table_args__ = (
        UniqueConstraint("document_id", "tag_id", name="uq_document_tags_document_id_tag_id"),
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Document(Base):
    """Archiviertes Dokument mit Nextcloud-Link und Suchvektor."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    document_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    nextcloud_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    nextcloud_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            "setweight(to_tsvector('german', coalesce(title, '')), 'A') || "
            "setweight(to_tsvector('german', coalesce(summary, '')), 'B') || "
            "setweight(to_tsvector('german', coalesce(original_filename, '')), 'C')",
            persisted=True,
        ),
        nullable=True,
    )

    tags: Mapped[List["Tag"]] = relationship(
        secondary="document_tags",
        back_populates="documents",
        lazy="selectin",
    )


class Tag(Base):
    """Tag zur Kategorisierung von Dokumenten."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    color: Mapped[str | None] = mapped_column(String(32), nullable=True)

    documents: Mapped[List[Document]] = relationship(
        secondary="document_tags",
        back_populates="tags",
        lazy="selectin",
    )

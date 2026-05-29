"""SQLAlchemy-Domain-Models fuer Dokumente, Tags, Korrespondenten und Dokumenttypen."""

from datetime import date, datetime
from typing import List

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Gemeinsame deklarative SQLAlchemy-Basis fuer alle ORM-Models."""


class Correspondent(Base):
    """Korrespondent (Absender/Empfaenger) eines Dokuments."""

    __tablename__ = "correspondents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    documents: Mapped[List["Document"]] = relationship(
        back_populates="correspondent",
        lazy="selectin",
    )


class DocumentType(Base):
    """Dokumenttyp zur Kategorisierung (z.B. Rechnung, Vertrag, Antrag)."""

    __tablename__ = "document_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    color: Mapped[str | None] = mapped_column(String(32), nullable=True)

    documents: Mapped[List["Document"]] = relationship(
        back_populates="document_type_rel",
        lazy="selectin",
    )


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
    document_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("document_types.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    correspondent_id: Mapped[int | None] = mapped_column(
        ForeignKey("correspondents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
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
        nullable=True,
    )

    document_type_rel: Mapped["DocumentType | None"] = relationship(
        back_populates="documents",
        lazy="joined",
    )
    correspondent: Mapped["Correspondent | None"] = relationship(
        back_populates="documents",
        lazy="joined",
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

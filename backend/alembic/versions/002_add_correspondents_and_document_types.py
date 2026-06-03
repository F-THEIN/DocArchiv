"""Fehlende Tabellen correspondents und document_types nachtragen.

Reparatur-Migration: Die initiale Migration 001 wurde ausgefuehrt, bevor
correspondents und document_types darin enthalten waren. Diese Migration
fuegt die fehlenden Tabellen, Spalten, FK-Constraints, Indizes und
Trigger-Funktionen nach – aber nur, wenn sie noch nicht existieren.

Bei frischen Installationen (wo 001 bereits alles erstellt hat) ist diese
Migration ein No-Op.

Revision ID: 002_add_corr_doctype
Revises: 001_initial_schema
Create Date: 2026-05-29 12:35:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002_add_corr_doctype"
down_revision: str | None = "001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_exists(table_name: str) -> bool:
    """Prueft, ob eine Tabelle in der Datenbank existiert."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS ("
            "  SELECT 1 FROM information_schema.tables"
            "  WHERE table_schema = 'public' AND table_name = :tbl"
            ")"
        ),
        {"tbl": table_name},
    )
    return result.scalar()  # type: ignore[return-value]


def _column_exists(table_name: str, column_name: str) -> bool:
    """Prueft, ob eine Spalte in einer Tabelle existiert."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS ("
            "  SELECT 1 FROM information_schema.columns"
            "  WHERE table_schema = 'public'"
            "    AND table_name = :tbl"
            "    AND column_name = :col"
            ")"
        ),
        {"tbl": table_name, "col": column_name},
    )
    return result.scalar()  # type: ignore[return-value]


def upgrade() -> None:
    """Erstellt correspondents, document_types und ergaenzt documents um FKs."""

    # --- Korrespondenten (nur erstellen, wenn nicht vorhanden) ---
    if not _table_exists("correspondents"):
        op.create_table(
            "correspondents",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name", name="uq_correspondents_name"),
        )
        op.create_index("ix_correspondents_name", "correspondents", ["name"], unique=True)

    # --- Dokumenttypen (nur erstellen, wenn nicht vorhanden) ---
    if not _table_exists("document_types"):
        op.create_table(
            "document_types",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("color", sa.String(length=32), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name", name="uq_document_types_name"),
        )
        op.create_index("ix_document_types_name", "document_types", ["name"], unique=True)

    # --- Fehlende Spalten in documents hinzufuegen ---
    if not _column_exists("documents", "document_type_id"):
        op.add_column(
            "documents",
            sa.Column("document_type_id", sa.Integer(), nullable=True),
        )
        op.create_foreign_key(
            "fk_documents_document_type_id",
            "documents",
            "document_types",
            ["document_type_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        op.create_index(
            "ix_documents_document_type_id", "documents", ["document_type_id"], unique=False
        )

    if not _column_exists("documents", "correspondent_id"):
        op.add_column(
            "documents",
            sa.Column("correspondent_id", sa.Integer(), nullable=True),
        )
        op.create_foreign_key(
            "fk_documents_correspondent_id",
            "documents",
            "correspondents",
            ["correspondent_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_index(
            "ix_documents_correspondent_id", "documents", ["correspondent_id"], unique=False
        )

    # --- Trigger: Korrespondent-Namensaenderung ---
    op.execute(
        """
        CREATE OR REPLACE FUNCTION correspondents_name_update() RETURNS trigger AS $$
        BEGIN
            IF OLD.name IS DISTINCT FROM NEW.name THEN
                UPDATE documents SET updated_at = now() WHERE correspondent_id = NEW.id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute("DROP TRIGGER IF EXISTS trg_correspondents_name_update ON correspondents")
    op.execute(
        """
        CREATE TRIGGER trg_correspondents_name_update
        AFTER UPDATE ON correspondents
        FOR EACH ROW
        EXECUTE FUNCTION correspondents_name_update();
        """
    )

    # --- Trigger: Dokumenttyp-Namensaenderung ---
    op.execute(
        """
        CREATE OR REPLACE FUNCTION document_types_name_update() RETURNS trigger AS $$
        BEGIN
            IF OLD.name IS DISTINCT FROM NEW.name THEN
                UPDATE documents SET updated_at = now() WHERE document_type_id = NEW.id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute("DROP TRIGGER IF EXISTS trg_document_types_name_update ON document_types")
    op.execute(
        """
        CREATE TRIGGER trg_document_types_name_update
        AFTER UPDATE ON document_types
        FOR EACH ROW
        EXECUTE FUNCTION document_types_name_update();
        """
    )


def downgrade() -> None:
    """Entfernt die in dieser Migration erstellten Objekte.

    Hinweis: Bei frischen Installationen (wo 001 alles erstellt hat) kann
    der Downgrade fehlschlagen, da die Constraints andere Namen haben.
    """
    op.execute("DROP TRIGGER IF EXISTS trg_document_types_name_update ON document_types")
    op.execute("DROP FUNCTION IF EXISTS document_types_name_update()")
    op.execute("DROP TRIGGER IF EXISTS trg_correspondents_name_update ON correspondents")
    op.execute("DROP FUNCTION IF EXISTS correspondents_name_update()")

    # Nur Spalten/Tabellen entfernen, die von dieser Migration erstellt wurden
    if _column_exists("documents", "correspondent_id"):
        op.drop_constraint("fk_documents_correspondent_id", "documents", type_="foreignkey")
        op.drop_index("ix_documents_correspondent_id", table_name="documents")
        op.drop_column("documents", "correspondent_id")

    if _column_exists("documents", "document_type_id"):
        op.drop_constraint("fk_documents_document_type_id", "documents", type_="foreignkey")
        op.drop_index("ix_documents_document_type_id", table_name="documents")
        op.drop_column("documents", "document_type_id")

    if _table_exists("document_types"):
        op.drop_index("ix_document_types_name", table_name="document_types")
        op.drop_table("document_types")

    if _table_exists("correspondents"):
        op.drop_index("ix_correspondents_name", table_name="correspondents")
        op.drop_table("correspondents")

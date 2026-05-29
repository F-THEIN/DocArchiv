"""Initiales Datenbankschema fuer DocArchiv.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-05-29 11:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Erstellt Tabellen, Relationen, Volltextsuche-Trigger und Indizes."""

    # --- Korrespondenten ---
    op.create_table(
        "correspondents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_correspondents_name"),
    )
    op.create_index("ix_correspondents_name", "correspondents", ["name"], unique=True)

    # --- Dokumenttypen ---
    op.create_table(
        "document_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("color", sa.String(length=32), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_document_types_name"),
    )
    op.create_index("ix_document_types_name", "document_types", ["name"], unique=True)

    # --- Dokumente ---
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("document_type_id", sa.Integer(), nullable=False),
        sa.Column("correspondent_id", sa.Integer(), nullable=True),
        sa.Column("document_date", sa.Date(), nullable=True),
        sa.Column("nextcloud_path", sa.String(length=1024), nullable=False),
        sa.Column("nextcloud_url", sa.String(length=2048), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["document_type_id"], ["document_types.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["correspondent_id"], ["correspondents.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_documents_title", "documents", ["title"], unique=False)
    op.create_index("ix_documents_document_type_id", "documents", ["document_type_id"], unique=False)
    op.create_index("ix_documents_correspondent_id", "documents", ["correspondent_id"], unique=False)
    op.create_index("ix_documents_document_date", "documents", ["document_date"], unique=False)
    op.create_index("idx_documents_search", "documents", ["search_vector"], unique=False, postgresql_using="gin")

    # --- Tags ---
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("color", sa.String(length=32), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_tags_name"),
    )
    op.create_index("ix_tags_name", "tags", ["name"], unique=True)

    # --- Document-Tags (M:N) ---
    op.create_table(
        "document_tags",
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("document_id", "tag_id"),
        sa.UniqueConstraint("document_id", "tag_id", name="uq_document_tags_document_id_tag_id"),
    )

    # --- Trigger-Funktion fuer search_vector ---
    # Baut den Suchvektor aus title, summary, original_filename sowie den
    # Namen von Dokumenttyp und Korrespondent zusammen.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION documents_search_vector_update() RETURNS trigger AS $$
        DECLARE
            v_type_name TEXT;
            v_corr_name TEXT;
        BEGIN
            SELECT name INTO v_type_name FROM document_types WHERE id = NEW.document_type_id;
            IF NEW.correspondent_id IS NOT NULL THEN
                SELECT name INTO v_corr_name FROM correspondents WHERE id = NEW.correspondent_id;
            ELSE
                v_corr_name := '';
            END IF;

            NEW.search_vector :=
                setweight(to_tsvector('german', coalesce(NEW.title, '')), 'A') ||
                setweight(to_tsvector('german', coalesce(NEW.summary, '')), 'B') ||
                setweight(to_tsvector('german', coalesce(v_corr_name, '')), 'B') ||
                setweight(to_tsvector('german', coalesce(v_type_name, '')), 'C') ||
                setweight(to_tsvector('german', coalesce(NEW.original_filename, '')), 'C');

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # Trigger auf documents bei INSERT oder UPDATE
    op.execute(
        """
        CREATE TRIGGER trg_documents_search_vector
        BEFORE INSERT OR UPDATE ON documents
        FOR EACH ROW
        EXECUTE FUNCTION documents_search_vector_update();
        """
    )

    # Trigger auf correspondents: Bei Namensaenderung search_vector aller
    # zugehoerigen Dokumente aktualisieren.
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
    op.execute(
        """
        CREATE TRIGGER trg_correspondents_name_update
        AFTER UPDATE ON correspondents
        FOR EACH ROW
        EXECUTE FUNCTION correspondents_name_update();
        """
    )

    # Trigger auf document_types: Bei Namensaenderung search_vector aller
    # zugehoerigen Dokumente aktualisieren.
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
    op.execute(
        """
        CREATE TRIGGER trg_document_types_name_update
        AFTER UPDATE ON document_types
        FOR EACH ROW
        EXECUTE FUNCTION document_types_name_update();
        """
    )


def downgrade() -> None:
    """Entfernt Trigger, Funktionen, Tabellen und Indizes."""
    op.execute("DROP TRIGGER IF EXISTS trg_document_types_name_update ON document_types")
    op.execute("DROP FUNCTION IF EXISTS document_types_name_update()")
    op.execute("DROP TRIGGER IF EXISTS trg_correspondents_name_update ON correspondents")
    op.execute("DROP FUNCTION IF EXISTS correspondents_name_update()")
    op.execute("DROP TRIGGER IF EXISTS trg_documents_search_vector ON documents")
    op.execute("DROP FUNCTION IF EXISTS documents_search_vector_update()")

    op.drop_table("document_tags")
    op.drop_index("ix_tags_name", table_name="tags")
    op.drop_table("tags")
    op.drop_index("idx_documents_search", table_name="documents", postgresql_using="gin")
    op.drop_index("ix_documents_document_date", table_name="documents")
    op.drop_index("ix_documents_correspondent_id", table_name="documents")
    op.drop_index("ix_documents_document_type_id", table_name="documents")
    op.drop_index("ix_documents_title", table_name="documents")
    op.drop_table("documents")
    op.drop_index("ix_document_types_name", table_name="document_types")
    op.drop_table("document_types")
    op.drop_index("ix_correspondents_name", table_name="correspondents")
    op.drop_table("correspondents")

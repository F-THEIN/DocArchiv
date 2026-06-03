"""search_vector von Trigger-basiert auf GENERATED ALWAYS AS ... STORED umstellen.

Die bisherige Implementierung nutzte einen BEFORE-Trigger, der
NEW.search_vector bei INSERT/UPDATE setzte. Das ORM-Model deklariert die
Spalte jetzt als Computed (GENERATED ALWAYS), was mit dem Trigger
inkompatibel ist. Diese Migration raeumt den alten Trigger auf und baut
die Spalte als echte Generated Column um.

Revision ID: 003_search_vector_generated
Revises: 002_add_corr_doctype
Create Date: 2026-06-03 13:50:00.000000
"""

from collections.abc import Sequence

from alembic import op

revision: str = "003_search_vector_generated"
down_revision: str | None = "002_add_corr_doctype"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Entfernt den alten Trigger und baut search_vector als Generated Column um."""

    # --- Alten Trigger und Funktion entfernen (idempotent) ---
    op.execute("DROP TRIGGER IF EXISTS trg_documents_search_vector ON documents")
    op.execute("DROP FUNCTION IF EXISTS documents_search_vector_update()")

    # --- Spalte droppen und als GENERATED ALWAYS neu erstellen ---
    op.execute("DROP INDEX IF EXISTS idx_documents_search")
    op.execute("ALTER TABLE documents DROP COLUMN IF EXISTS search_vector")
    op.execute(
        """
        ALTER TABLE documents ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('german', coalesce(title, '')), 'A') ||
            setweight(to_tsvector('german', coalesce(summary, '')), 'B') ||
            setweight(to_tsvector('german', coalesce(original_filename, '')), 'C')
        ) STORED
        """
    )
    op.execute(
        "CREATE INDEX idx_documents_search ON documents USING gin(search_vector)"
    )


def downgrade() -> None:
    """Stellt die Trigger-basierte search_vector-Spalte wieder her."""

    # --- Generated Column entfernen ---
    op.execute("DROP INDEX IF EXISTS idx_documents_search")
    op.execute("ALTER TABLE documents DROP COLUMN IF EXISTS search_vector")

    # --- Normale TSVECTOR-Spalte + Trigger wiederherstellen ---
    op.execute("ALTER TABLE documents ADD COLUMN search_vector tsvector")
    op.execute(
        "CREATE INDEX idx_documents_search ON documents USING gin(search_vector)"
    )
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
    op.execute(
        """
        CREATE TRIGGER trg_documents_search_vector
        BEFORE INSERT OR UPDATE ON documents
        FOR EACH ROW
        EXECUTE FUNCTION documents_search_vector_update();
        """
    )

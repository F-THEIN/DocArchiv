"""Repository-Klassen fuer gekapselte Datenbankzugriffe."""

from datetime import date
from typing import Literal

from sqlalchemy import Select, and_, asc, desc, distinct, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from domain.models import Correspondent, Document, DocumentTag, DocumentType, Tag

DocumentSort = Literal[
    "date_desc",
    "date_asc",
    "created_desc",
    "created_asc",
    "title_asc",
    "title_desc",
    "relevance",
]


class CorrespondentRepository:
    """Kapselt Datenbankzugriffe fuer Korrespondenten."""

    def __init__(self, session: Session) -> None:
        """Initialisiert das Repository mit einer SQLAlchemy-Session."""
        self.session = session

    def get_by_id(self, correspondent_id: int) -> Correspondent | None:
        """Liefert einen Korrespondenten anhand seiner ID."""
        return self.session.get(Correspondent, correspondent_id)

    def get_by_name(self, name: str) -> Correspondent | None:
        """Liefert einen Korrespondenten anhand seines Namens."""
        statement = select(Correspondent).where(Correspondent.name == name.strip())
        return self.session.scalars(statement).first()

    def get_or_create(self, name: str) -> Correspondent:
        """Liefert einen vorhandenen Korrespondenten oder erstellt ihn."""
        normalized_name = name.strip()
        correspondent = self.get_by_name(normalized_name)
        if correspondent is not None:
            return correspondent
        return self.create(Correspondent(name=normalized_name))

    def create(self, correspondent: Correspondent) -> Correspondent:
        """Fuegt einen Korrespondenten der Session hinzu und flusht ihn."""
        self.session.add(correspondent)
        self.session.flush()
        self.session.refresh(correspondent)
        return correspondent

    def update(self, correspondent: Correspondent) -> Correspondent:
        """Flusht einen geaenderten Korrespondenten und gibt ihn zurueck."""
        self.session.flush()
        self.session.refresh(correspondent)
        return correspondent

    def delete(self, correspondent: Correspondent) -> None:
        """Loescht einen Korrespondenten aus der Session."""
        self.session.delete(correspondent)
        self.session.flush()

    def list_with_document_counts(self) -> list[tuple[Correspondent, int]]:
        """Liefert alle Korrespondenten mit zugehoeriger Dokumentanzahl."""
        statement = (
            select(Correspondent, func.count(Document.id).label("document_count"))
            .outerjoin(Document, Correspondent.id == Document.correspondent_id)
            .group_by(Correspondent.id)
            .order_by(asc(Correspondent.name))
        )
        return [
            (correspondent, int(document_count))
            for correspondent, document_count in self.session.execute(statement).all()
        ]


class DocumentTypeRepository:
    """Kapselt Datenbankzugriffe fuer Dokumenttypen."""

    def __init__(self, session: Session) -> None:
        """Initialisiert das Repository mit einer SQLAlchemy-Session."""
        self.session = session

    def get_by_id(self, document_type_id: int) -> DocumentType | None:
        """Liefert einen Dokumenttyp anhand seiner ID."""
        return self.session.get(DocumentType, document_type_id)

    def get_by_name(self, name: str) -> DocumentType | None:
        """Liefert einen Dokumenttyp anhand seines Namens."""
        statement = select(DocumentType).where(DocumentType.name == name.strip())
        return self.session.scalars(statement).first()

    def get_or_create(self, name: str, color: str | None = None) -> DocumentType:
        """Liefert einen vorhandenen Dokumenttyp oder erstellt ihn."""
        normalized_name = name.strip()
        document_type = self.get_by_name(normalized_name)
        if document_type is not None:
            return document_type
        return self.create(DocumentType(name=normalized_name, color=color))

    def create(self, document_type: DocumentType) -> DocumentType:
        """Fuegt einen Dokumenttyp der Session hinzu und flusht ihn."""
        self.session.add(document_type)
        self.session.flush()
        self.session.refresh(document_type)
        return document_type

    def update(self, document_type: DocumentType) -> DocumentType:
        """Flusht einen geaenderten Dokumenttyp und gibt ihn zurueck."""
        self.session.flush()
        self.session.refresh(document_type)
        return document_type

    def delete(self, document_type: DocumentType) -> None:
        """Loescht einen Dokumenttyp aus der Session."""
        self.session.delete(document_type)
        self.session.flush()

    def list_with_document_counts(self) -> list[tuple[DocumentType, int]]:
        """Liefert alle Dokumenttypen mit zugehoeriger Dokumentanzahl."""
        statement = (
            select(DocumentType, func.count(Document.id).label("document_count"))
            .outerjoin(Document, DocumentType.id == Document.document_type_id)
            .group_by(DocumentType.id)
            .order_by(asc(DocumentType.name))
        )
        return [
            (document_type, int(document_count))
            for document_type, document_count in self.session.execute(statement).all()
        ]


class DocumentRepository:
    """Kapselt Datenbankzugriffe fuer Dokumente."""

    def __init__(self, session: Session) -> None:
        """Initialisiert das Repository mit einer SQLAlchemy-Session."""
        self.session = session

    def get_by_id(self, document_id: int) -> Document | None:
        """Liefert ein Dokument anhand seiner ID inklusive Relationen."""
        statement = (
            select(Document)
            .options(
                joinedload(Document.document_type_rel),
                joinedload(Document.correspondent),
                selectinload(Document.tags),
            )
            .where(Document.id == document_id)
        )
        return self.session.scalars(statement).first()

    def list_documents(
        self,
        *,
        q: str | None = None,
        tags: list[str] | None = None,
        document_type_id: int | None = None,
        correspondent_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        per_page: int = 25,
        sort: DocumentSort = "date_desc",
    ) -> tuple[list[Document], int]:
        """Liefert gefilterte und paginierte Dokumente mit Gesamtanzahl."""
        filters = self._build_filters(
            q=q,
            tags=tags or [],
            document_type_id=document_type_id,
            correspondent_id=correspondent_id,
            date_from=date_from,
            date_to=date_to,
        )

        statement = select(Document).options(
            joinedload(Document.document_type_rel),
            joinedload(Document.correspondent),
            selectinload(Document.tags),
        )
        count_statement = select(func.count(Document.id))

        if filters:
            statement = statement.where(and_(*filters))
            count_statement = count_statement.where(and_(*filters))

        statement = self._apply_sort(statement, sort=sort, q=q)
        statement = statement.offset((page - 1) * per_page).limit(per_page)

        total = self.session.scalar(count_statement) or 0
        documents = list(self.session.scalars(statement).unique().all())
        return documents, total

    def create(self, document: Document) -> Document:
        """Fuegt ein Dokument der Session hinzu und flusht es."""
        self.session.add(document)
        self.session.flush()
        self.session.refresh(document)
        return document

    def delete(self, document: Document) -> None:
        """Loescht ein Dokument aus der Session."""
        self.session.delete(document)
        self.session.flush()

    def _build_filters(
        self,
        *,
        q: str | None,
        tags: list[str],
        document_type_id: int | None,
        correspondent_id: int | None,
        date_from: date | None,
        date_to: date | None,
    ) -> list[object]:
        """Erstellt SQLAlchemy-Filter fuer Suche und Facetten."""
        filters: list[object] = []

        if q:
            search_query = func.websearch_to_tsquery("german", q)
            filters.append(Document.search_vector.op("@@")(search_query))

        if tags:
            tag_subquery = (
                select(DocumentTag.document_id)
                .join(Tag, Tag.id == DocumentTag.tag_id)
                .where(Tag.name.in_(tags))
                .group_by(DocumentTag.document_id)
                .having(func.count(distinct(Tag.name)) == len(set(tags)))
            )
            filters.append(Document.id.in_(tag_subquery))

        if document_type_id is not None:
            filters.append(Document.document_type_id == document_type_id)

        if correspondent_id is not None:
            filters.append(Document.correspondent_id == correspondent_id)

        if date_from:
            filters.append(Document.document_date >= date_from)

        if date_to:
            filters.append(Document.document_date <= date_to)

        return filters

    def _apply_sort(self, statement: Select[tuple[Document]], *, sort: DocumentSort, q: str | None) -> Select[tuple[Document]]:
        """Wendet die gewuenschte Sortierung auf eine Dokumentenabfrage an."""
        if sort == "title_asc":
            return statement.order_by(asc(Document.title))
        if sort == "title_desc":
            return statement.order_by(desc(Document.title))
        if sort == "created_asc":
            return statement.order_by(asc(Document.created_at))
        if sort == "created_desc":
            return statement.order_by(desc(Document.created_at))
        if sort == "date_asc":
            return statement.order_by(asc(Document.document_date).nulls_last(), asc(Document.created_at))
        if sort == "relevance" and q:
            search_query = func.websearch_to_tsquery("german", q)
            rank = func.ts_rank_cd(Document.search_vector, search_query)
            return statement.order_by(desc(rank), desc(Document.document_date).nulls_last(), desc(Document.created_at))

        return statement.order_by(desc(Document.document_date).nulls_last(), desc(Document.created_at))


class TagRepository:
    """Kapselt Datenbankzugriffe fuer Tags."""

    def __init__(self, session: Session) -> None:
        """Initialisiert das Repository mit einer SQLAlchemy-Session."""
        self.session = session

    def get_by_id(self, tag_id: int) -> Tag | None:
        """Liefert einen Tag anhand seiner ID."""
        return self.session.get(Tag, tag_id)

    def get_by_name(self, name: str) -> Tag | None:
        """Liefert einen Tag anhand seines normalisierten Namens."""
        statement = select(Tag).where(Tag.name == name.strip().lower())
        return self.session.scalars(statement).first()

    def get_many_by_names(self, names: list[str]) -> list[Tag]:
        """Liefert mehrere Tags anhand ihrer normalisierten Namen."""
        normalized_names = sorted({name.strip().lower() for name in names if name.strip()})
        if not normalized_names:
            return []
        statement = select(Tag).where(Tag.name.in_(normalized_names)).order_by(asc(Tag.name))
        return list(self.session.scalars(statement).all())

    def create(self, tag: Tag) -> Tag:
        """Fuegt einen Tag der Session hinzu und flusht ihn."""
        self.session.add(tag)
        self.session.flush()
        self.session.refresh(tag)
        return tag

    def get_or_create(self, name: str, color: str | None = None) -> Tag:
        """Liefert einen vorhandenen Tag oder erstellt ihn."""
        normalized_name = name.strip().lower()
        tag = self.get_by_name(normalized_name)
        if tag is not None:
            return tag
        return self.create(Tag(name=normalized_name, color=color))

    def list_with_document_counts(self) -> list[tuple[Tag, int]]:
        """Liefert alle Tags mit zugehoeriger Dokumentanzahl."""
        statement = (
            select(Tag, func.count(DocumentTag.document_id).label("document_count"))
            .outerjoin(DocumentTag, Tag.id == DocumentTag.tag_id)
            .group_by(Tag.id)
            .order_by(asc(Tag.name))
        )
        return [(tag, int(document_count)) for tag, document_count in self.session.execute(statement).all()]

    def delete(self, tag: Tag) -> None:
        """Loescht einen Tag aus der Session."""
        self.session.delete(tag)
        self.session.flush()

    def update(self, tag: Tag) -> Tag:
        """Flusht einen geaenderten Tag und gibt ihn zurueck."""
        self.session.flush()
        self.session.refresh(tag)
        return tag

"""HTTP-Endpunkte fuer Dokumente."""

from datetime import date

from fastapi import APIRouter, HTTPException, Query, status

from api.dependencies import DocumentServiceDep
from domain.schemas import (
    DocumentCreate,
    DocumentListResponse,
    DocumentQueryParams,
    DocumentResponse,
    DocumentUpdate,
    PaginatedResponse,
)
from domain.services import DocumentNotFoundError

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=PaginatedResponse[DocumentListResponse])
def list_documents(
    service: DocumentServiceDep,
    q: str | None = Query(default=None, description="Volltextsuche"),
    tags: str | None = Query(default=None, description="Kommaseparierte Tag-Liste"),
    document_type_id: int | None = Query(default=None, description="Dokumenttyp-ID"),
    correspondent_id: int | None = Query(default=None, description="Korrespondent-ID"),
    date_from: date | None = Query(default=None, description="Startdatum inklusive"),
    date_to: date | None = Query(default=None, description="Enddatum inklusive"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=25, ge=1, le=100),
    sort: str = Query(default="date_desc"),
) -> PaginatedResponse[DocumentListResponse]:
    """Liefert Dokumente mit Suche, Filtern, Pagination und Sortierung."""
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    query = DocumentQueryParams(
        q=q,
        tags=tag_list,
        document_type_id=document_type_id,
        correspondent_id=correspondent_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        per_page=per_page,
        sort=sort,
    )
    return service.list_documents(query)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, service: DocumentServiceDep) -> DocumentResponse:
    """Liefert ein einzelnes Dokument anhand seiner ID."""
    try:
        return service.get_document(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(data: DocumentCreate, service: DocumentServiceDep) -> DocumentResponse:
    """Legt ein neues Dokument an."""
    return service.create_document(data)


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(document_id: int, data: DocumentUpdate, service: DocumentServiceDep) -> DocumentResponse:
    """Aktualisiert ein vorhandenes Dokument teilweise."""
    try:
        return service.update_document(document_id, data)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, service: DocumentServiceDep) -> None:
    """Loescht ein Dokument."""
    try:
        service.delete_document(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

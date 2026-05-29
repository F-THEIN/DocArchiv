"""HTTP-Endpunkte fuer Dokumenttypen."""

from fastapi import APIRouter, HTTPException, status

from api.dependencies import DocumentTypeServiceDep
from domain.schemas import DocumentTypeCreate, DocumentTypeResponse, DocumentTypeUpdate
from domain.services import DocumentTypeNotFoundError

router = APIRouter(prefix="/document-types", tags=["document-types"])


@router.get("", response_model=list[DocumentTypeResponse])
def list_document_types(service: DocumentTypeServiceDep) -> list[DocumentTypeResponse]:
    """Liefert alle Dokumenttypen inklusive Dokumentanzahl."""
    return service.list_document_types()


@router.post("", response_model=DocumentTypeResponse, status_code=status.HTTP_201_CREATED)
def create_document_type(data: DocumentTypeCreate, service: DocumentTypeServiceDep) -> DocumentTypeResponse:
    """Legt einen neuen Dokumenttyp an."""
    return service.create_document_type(data)


@router.get("/{document_type_id}", response_model=DocumentTypeResponse)
def get_document_type(document_type_id: int, service: DocumentTypeServiceDep) -> DocumentTypeResponse:
    """Liefert einen einzelnen Dokumenttyp anhand seiner ID."""
    try:
        return service.get_document_type(document_type_id)
    except DocumentTypeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{document_type_id}", response_model=DocumentTypeResponse)
def update_document_type(
    document_type_id: int, data: DocumentTypeUpdate, service: DocumentTypeServiceDep
) -> DocumentTypeResponse:
    """Aktualisiert einen vorhandenen Dokumenttyp teilweise."""
    try:
        return service.update_document_type(document_type_id, data)
    except DocumentTypeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{document_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_type(document_type_id: int, service: DocumentTypeServiceDep) -> None:
    """Loescht einen Dokumenttyp."""
    try:
        service.delete_document_type(document_type_id)
    except DocumentTypeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

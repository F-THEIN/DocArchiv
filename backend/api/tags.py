"""HTTP-Endpunkte fuer Tags."""

from fastapi import APIRouter, HTTPException, status

from api.dependencies import TagServiceDep
from domain.schemas import TagCreate, TagResponse, TagUpdate
from domain.services import TagNotFoundError

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagResponse])
def list_tags(service: TagServiceDep) -> list[TagResponse]:
    """Liefert alle Tags inklusive Dokumentanzahl."""
    return service.list_tags()


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(data: TagCreate, service: TagServiceDep) -> TagResponse:
    """Legt einen Tag an oder liefert den vorhandenen Tag zurueck."""
    return service.create_tag(data)


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, service: TagServiceDep) -> TagResponse:
    """Liefert einen Tag anhand seiner ID."""
    try:
        return service.get_tag(tag_id)
    except TagNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{tag_id}", response_model=TagResponse)
def update_tag(tag_id: int, data: TagUpdate, service: TagServiceDep) -> TagResponse:
    """Aktualisiert Name oder Farbe eines Tags."""
    try:
        return service.update_tag(tag_id, data)
    except TagNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, service: TagServiceDep) -> None:
    """Loescht einen Tag."""
    try:
        service.delete_tag(tag_id)
    except TagNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

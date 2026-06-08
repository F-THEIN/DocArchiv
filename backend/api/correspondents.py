"""HTTP-Endpunkte fuer Korrespondenten."""

from fastapi import APIRouter, HTTPException, status

from api.dependencies import CorrespondentServiceDep
from domain.schemas import CorrespondentCreate, CorrespondentMerge, CorrespondentMergeResponse, CorrespondentResponse, CorrespondentUpdate
from domain.services import CorrespondentNotFoundError

router = APIRouter(prefix="/correspondents", tags=["correspondents"])


@router.get("", response_model=list[CorrespondentResponse])
def list_correspondents(service: CorrespondentServiceDep) -> list[CorrespondentResponse]:
    """Liefert alle Korrespondenten inklusive Dokumentanzahl."""
    return service.list_correspondents()


@router.post("", response_model=CorrespondentResponse, status_code=status.HTTP_201_CREATED)
def create_correspondent(data: CorrespondentCreate, service: CorrespondentServiceDep) -> CorrespondentResponse:
    """Legt einen neuen Korrespondenten an."""
    return service.create_correspondent(data)


@router.get("/{correspondent_id}", response_model=CorrespondentResponse)
def get_correspondent(correspondent_id: int, service: CorrespondentServiceDep) -> CorrespondentResponse:
    """Liefert einen einzelnen Korrespondenten anhand seiner ID."""
    try:
        return service.get_correspondent(correspondent_id)
    except CorrespondentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{correspondent_id}", response_model=CorrespondentResponse)
def update_correspondent(
    correspondent_id: int, data: CorrespondentUpdate, service: CorrespondentServiceDep
) -> CorrespondentResponse:
    """Aktualisiert einen vorhandenen Korrespondenten teilweise."""
    try:
        return service.update_correspondent(correspondent_id, data)
    except CorrespondentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{correspondent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_correspondent(correspondent_id: int, service: CorrespondentServiceDep) -> None:
    """Loescht einen Korrespondenten."""
    try:
        service.delete_correspondent(correspondent_id)
    except CorrespondentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/merge", response_model=CorrespondentMergeResponse)
def merge_correspondents(data: CorrespondentMerge, service: CorrespondentServiceDep) -> CorrespondentMergeResponse:
    """Fuehrt mehrere Korrespondenten zu einem Ziel zusammen."""
    try:
        return service.merge_correspondents(data)
    except CorrespondentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

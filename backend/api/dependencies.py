"""FastAPI-Dependencies fuer Services und Datenbankzugriff."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from config import Settings, get_settings
from domain.services import AdminService, CorrespondentService, DocumentService, DocumentTypeService, TagService
from infrastructure.database import get_db_session
from infrastructure.repositories import (
    CorrespondentRepository,
    DocumentRepository,
    DocumentTypeRepository,
    TagRepository,
)

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[Session, Depends(get_db_session)]


def get_correspondent_service(session: SessionDep) -> CorrespondentService:
    """Erzeugt den CorrespondentService fuer einen Request."""
    return CorrespondentService(
        correspondent_repository=CorrespondentRepository(session),
        session=session,
    )


def get_document_type_service(session: SessionDep) -> DocumentTypeService:
    """Erzeugt den DocumentTypeService fuer einen Request."""
    return DocumentTypeService(
        document_type_repository=DocumentTypeRepository(session),
        session=session,
    )


def get_document_service(session: SessionDep, settings: SettingsDep) -> DocumentService:
    """Erzeugt den DocumentService fuer einen Request."""
    return DocumentService(
        document_repository=DocumentRepository(session),
        tag_repository=TagRepository(session),
        session=session,
        nextcloud_base_url=settings.nextcloud_base_url,
    )


def get_tag_service(session: SessionDep) -> TagService:
    """Erzeugt den TagService fuer einen Request."""
    return TagService(
        tag_repository=TagRepository(session),
        session=session,
    )


def get_admin_service(session: SessionDep) -> AdminService:
    """Erzeugt den AdminService fuer einen Request."""
    return AdminService(session=session)


CorrespondentServiceDep = Annotated[CorrespondentService, Depends(get_correspondent_service)]
DocumentTypeServiceDep = Annotated[DocumentTypeService, Depends(get_document_type_service)]
DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]


def get_database_session() -> Generator[Session, None, None]:
    """Kompatibilitaets-Wrapper fuer direkte DB-Session-Dependencies."""
    yield from get_db_session()

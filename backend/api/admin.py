"""HTTP-Endpunkte fuer administrative Funktionen."""

from fastapi import APIRouter

from api.dependencies import AdminServiceDep
from domain.schemas import AdminStatsResponse, DatabaseInfoResponse, ResetDatabaseResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reset-database", response_model=ResetDatabaseResponse)
def reset_database(service: AdminServiceDep) -> ResetDatabaseResponse:
    """Setzt die Datenbank durch Loeschen aller Archivdaten zurueck."""
    return service.reset_database()


@router.get("/stats", response_model=AdminStatsResponse)
def get_stats(service: AdminServiceDep) -> AdminStatsResponse:
    """Liefert fachliche Statistiken fuer die Admin-Seite."""
    return service.get_stats()


@router.get("/database-info", response_model=DatabaseInfoResponse)
def get_database_info(service: AdminServiceDep) -> DatabaseInfoResponse:
    """Liefert technische Informationen zur Datenbank."""
    return service.get_database_info()

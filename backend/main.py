"""FastAPI-Einstiegspunkt fuer die DocArchiv-Anwendung."""

import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.admin import router as admin_router
from api.correspondents import router as correspondents_router
from api.document_types import router as document_types_router
from api.documents import router as documents_router
from api.tags import router as tags_router
from config import Settings, get_settings

logger = logging.getLogger(__name__)


def configure_logging(settings: Settings) -> None:
    """Konfiguriert das Python-Logging fuer die Anwendung."""
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def create_app() -> FastAPI:
    """Erstellt und konfiguriert die FastAPI-Anwendung."""
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Leichtgewichtiger Dokumenten-Katalog mit Volltextsuche und Nextcloud-Linkout.",
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(documents_router, prefix=settings.api_prefix)
    app.include_router(tags_router, prefix=settings.api_prefix)
    app.include_router(correspondents_router, prefix=settings.api_prefix)
    app.include_router(document_types_router, prefix=settings.api_prefix)
    app.include_router(admin_router, prefix=settings.api_prefix)

    @app.get(f"{settings.api_prefix}/health", tags=["health"])
    def health_check() -> dict[str, Any]:
        """Liefert den Health-Status der Anwendung."""
        return {
            "status": "ok",
            "service": settings.app_name,
            "version": settings.app_version,
        }

    mount_static_files(app, settings.static_dir)
    return app


def mount_static_files(app: FastAPI, static_dir: Path) -> None:
    """Mounted die gebaute SPA, falls sie im Runtime-Image vorhanden ist."""
    if not static_dir.exists():
        logger.info("Static-Verzeichnis %s existiert noch nicht; SPA-Serving wird uebersprungen.", static_dir)
        return

    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str) -> FileResponse:
        """Serviert statische SPA-Dateien oder faellt auf index.html zurueck."""
        requested_path = static_dir / full_path
        if full_path and requested_path.is_file():
            return FileResponse(requested_path)

        index_path = static_dir / "index.html"
        return FileResponse(index_path)


app = create_app()

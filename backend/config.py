"""Zentrale Anwendungskonfiguration fuer DocArchiv."""

from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Umgebungsbasierte Konfiguration der DocArchiv-Anwendung."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "DocArchiv"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    database_url: str = Field(
        default="postgresql://docarchiv:changeme@docarchiv-db:5432/docarchiv",
        alias="DATABASE_URL",
    )
    docarchiv_nc_base_url: AnyHttpUrl | str = Field(
        default="https://nextcloud.example.com/apps/files/?dir=/Documents/Scans",
        alias="DOCARCHIV_NC_BASE_URL",
    )
    static_dir: Path = Field(default=Path("static"), alias="DOCARCHIV_STATIC_DIR")
    log_level: str = Field(default="INFO", alias="DOCARCHIV_LOG_LEVEL")

    @property
    def nextcloud_base_url(self) -> str:
        """Gibt die Nextcloud-Basis-URL als String zurueck."""
        return str(self.docarchiv_nc_base_url).rstrip("/")


@lru_cache
def get_settings() -> Settings:
    """Liefert gecachte Anwendungseinstellungen."""
    return Settings()

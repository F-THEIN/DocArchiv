"""Datenbank-Engine und Session-Factory fuer DocArchiv."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import get_settings
from domain.models import Base

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db_session() -> Generator[Session, None, None]:
    """Erzeugt eine SQLAlchemy-Session fuer FastAPI-Dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

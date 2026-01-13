from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from ..core.config import get_settings
from .base import Base

BASE_BACKEND_DIR = Path(__file__).resolve().parents[2]


def _prepare_database(database_url: str) -> tuple[str, dict]:
    url = make_url(database_url)
    connect_args: dict = {}

    if url.drivername != "sqlite":
        return database_url, connect_args

    db_path = Path(url.database or "data/app.db")
    if not db_path.is_absolute():
        db_path = (BASE_BACKEND_DIR / db_path).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    updated_url = url.set(database=db_path.as_posix())
    connect_args = {"check_same_thread": False}
    return str(updated_url), connect_args


settings = get_settings()
database_url, connect_args = _prepare_database(settings.database_url)
engine = create_engine(database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session. Use Flask's g object for request-scoped sessions."""
    from flask import g
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db


def close_db(e=None):
    """Close database session at end of request."""
    from flask import g
    db = g.pop('db', None)
    if db is not None:
        db.close()


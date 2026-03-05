from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


def create_engine_from_url(database_url: str) -> Engine:
    """Create SQLAlchemy engine for SQLite/PostgreSQL-compatible URLs."""
    return create_engine(database_url, future=True)


def init_db(engine: Engine) -> None:
    """MVP initialization strategy: create all known tables."""
    Base.metadata.create_all(bind=engine)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

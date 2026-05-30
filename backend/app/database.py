"""Database engine, session factory and ORM base.

The module wires SQLAlchemy 2.x to the configured ``DATABASE_URL``. SQLite is
used by default for the demo, but the engine is created generically so a
Postgres URL works without code changes. A FastAPI dependency,
:func:`get_db`, yields a scoped session per request and guarantees cleanup.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# SQLite needs ``check_same_thread=False`` because FastAPI may use the
# connection across threads. Other databases ignore this argument.
_connect_args: dict[str, object] = (
    {"check_same_thread": False} if settings.is_sqlite else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session.

    The session is always closed when the request completes, even on error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all() -> None:
    """Create all tables declared on :class:`Base`.

    Used at startup for the demo in place of Alembic migrations. Importing the
    models module registers every table on ``Base.metadata`` before this runs.
    """
    # Import for side effects: ensures all models are registered with Base.
    from app import models  # noqa: F401  (registration side-effect)

    Base.metadata.create_all(bind=engine)

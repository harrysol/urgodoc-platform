"""SQLAlchemy engine, session factory and FastAPI dependency.

A single synchronous engine is shared by the API process and the Celery worker.
Synchronous SQLAlchemy is intentional: Celery tasks run in a plain (non-async)
worker process, and FastAPI executes sync path operations in a threadpool — so
one consistent session style keeps the data layer simple.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # transparently recycle dead connections
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a request-scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

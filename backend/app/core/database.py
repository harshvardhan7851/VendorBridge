"""
core/database.py
================
Async SQLAlchemy 2.0 engine, session factory, and Base re-export.

The declarative Base lives in app.models.base to avoid circular imports.
This module wires the engine to settings and provides get_db().
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# Re-export Base so legacy imports (from app.core.database import Base) still work
from app.models.base import Base  # noqa: F401

# ---------------------------------------------------------------------------
# Async Engine
# ---------------------------------------------------------------------------
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# ---------------------------------------------------------------------------
# Async Session Factory
# ---------------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ---------------------------------------------------------------------------
# FastAPI Dependency: get_db
# ---------------------------------------------------------------------------
async def get_db() -> AsyncSession:  # type: ignore[misc]
    """
    Yields an async DB session.
    Rolls back on exception; always closes the session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

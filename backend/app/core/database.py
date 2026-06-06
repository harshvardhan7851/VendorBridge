"""
Database Configuration
======================
Async SQLAlchemy 2.0 engine, session factory, and declarative base.

Provides:
  - async_engine     : AsyncEngine instance
  - AsyncSessionLocal: Session factory for dependency injection
  - Base             : Declarative base for all ORM models
  - get_db()         : FastAPI dependency to yield a DB session

Usage in a route:
    from app.core.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    @router.get("/example")
    async def example(db: AsyncSession = Depends(get_db)):
        # TODO: implement queries
        pass
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# ---------------------------------------------------------------------------
# Async Engine
# ---------------------------------------------------------------------------
# echo=True logs all SQL statements — useful in development, disable in prod
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,       # Verify connections before use
    pool_size=10,             # TODO: tune for production load
    max_overflow=20,
)

# ---------------------------------------------------------------------------
# Async Session Factory
# ---------------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,   # Prevents lazy-load errors after commit
    autocommit=False,
    autoflush=False,
)

# ---------------------------------------------------------------------------
# Declarative Base
# All ORM models should inherit from this Base.
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """
    Shared declarative base for all SQLAlchemy models.

    TODO: Add common timestamp columns (created_at, updated_at) here
          once the team decides on a shared mixin pattern.
    """
    pass


# ---------------------------------------------------------------------------
# Database Dependency (FastAPI)
# ---------------------------------------------------------------------------

async def get_db() -> AsyncSession:
    """
    FastAPI dependency that yields an async database session.
    The session is automatically closed after the request completes.

    Usage:
        async def my_endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # TODO: await session.commit() — call in service layer instead
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

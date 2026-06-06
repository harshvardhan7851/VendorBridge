"""
Alembic Environment Configuration
==================================
This file is loaded by Alembic when running migration commands.
It is configured for async SQLAlchemy (asyncpg driver).

Usage (inside Docker):
    docker compose exec backend alembic revision --autogenerate -m "initial"
    docker compose exec backend alembic upgrade head
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ---------------------------------------------------------------------------
# Import the declarative Base so Alembic can detect model changes
# ---------------------------------------------------------------------------
# TODO: Uncomment this once models are implemented
# from app.core.database import Base
# from app.models import *  # noqa: F401 — ensures all models are registered

# ---------------------------------------------------------------------------
# Alembic Config
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
# TODO: Replace None with Base.metadata once models are in place
target_metadata = None  # Base.metadata

# ---------------------------------------------------------------------------
# Offline Migrations (without a live DB connection)
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Generates SQL scripts without connecting to the database.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online Migrations (with a live async DB connection)
# ---------------------------------------------------------------------------

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode using an async engine.
    """
    # Read DATABASE_URL from environment (set in docker-compose.yml)
    import os
    db_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://vendorbridge:vendorbridge@postgres:5432/vendorbridge",
    )

    connectable = async_engine_from_config(
        {"sqlalchemy.url": db_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

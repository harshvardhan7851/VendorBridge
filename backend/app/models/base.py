"""
models/base.py
==============
Reusable TimestampMixin for all ORM models.
Provides: id (UUID PK), created_at, updated_at, updated_by.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base — imported by all models."""
    pass


class TimestampMixin:
    """
    Mixin that adds audit timestamp columns to any model.

    Columns:
        id         : UUID primary key, auto-generated.
        created_at : Set automatically on INSERT.
        updated_at : Updated automatically on UPDATE.
        updated_by : UUID of the user who last modified the record (nullable).
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

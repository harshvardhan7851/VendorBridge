"""
models/notification.py
======================
In-app notification model for workflow events.

Table:
  - notifications : User-targeted alerts for RFQ, quotation, and approval events.
"""

import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


# ---------------------------------------------------------------------------
# Enum: NotificationType
# ---------------------------------------------------------------------------

class NotificationType(str, enum.Enum):
    RFQ_INVITE           = "RFQ_INVITE"
    QUOTATION_RECEIVED   = "QUOTATION_RECEIVED"
    WINNER_SELECTED      = "WINNER_SELECTED"
    APPROVAL_REQUIRED    = "APPROVAL_REQUIRED"


# ---------------------------------------------------------------------------
# Model: Notification
# ---------------------------------------------------------------------------

class Notification(Base):
    """
    Stores in-app notifications targeted at individual users.

    entity_type / entity_id provide a lightweight polymorphic reference
    to the related domain object (e.g. type="rfq", id=<rfq_id>).
    """

    __tablename__ = "notifications"

    # --- Primary Key ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # --- Recipient ---
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # --- Content ---
    type: Mapped[NotificationType] = mapped_column(
        SAEnum(NotificationType, name="notificationtype", create_type=True),
        nullable=False,
        index=True,
    )

    message: Mapped[str] = mapped_column(Text, nullable=False)

    # --- Read State ---
    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # --- Polymorphic reference to related entity ---
    entity_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # e.g., "rfq", "quotation"

    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User",
        foreign_keys=[user_id],
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Notification id={self.id} type={self.type} user={self.user_id} read={self.is_read}>"

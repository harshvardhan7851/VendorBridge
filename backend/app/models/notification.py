"""
Notification Model
==================
In-app notifications sent to users for workflow events.
"""

import uuid
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # TODO: user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)

    notification_type = Column(
        SAEnum(
            "rfq_published", "quotation_submitted", "approval_required",
            "po_issued", "invoice_received", "general",
            name="notification_type",
        ),
        nullable=False,
        default="general",
    )

    # Reference to related entity (polymorphic pattern)
    related_entity_type = Column(String(50), nullable=True)   # e.g., "rfq", "po"
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)

    # TODO: user = relationship("User", back_populates="notifications")
    # TODO: Add created_at timestamp

    def __repr__(self) -> str:
        return f"<Notification id={self.id} type={self.notification_type} read={self.is_read}>"

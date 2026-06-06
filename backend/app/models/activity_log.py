"""
ActivityLog Model
=================
Audit trail for all significant actions performed in the system.
"""

import uuid
from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # TODO: user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    action = Column(String(100), nullable=False)       # e.g., "rfq.created", "vendor.approved"
    entity_type = Column(String(50), nullable=True)    # e.g., "rfq", "vendor"
    entity_id = Column(UUID(as_uuid=True), nullable=True)

    description = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)  # Extra context (IP, browser, etc.)

    # TODO: user = relationship("User", back_populates="activity_logs")
    # TODO: Add created_at timestamp

    def __repr__(self) -> str:
        return f"<ActivityLog id={self.id} action={self.action}>"

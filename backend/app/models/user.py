"""
User Model
==========
Represents a system user (Admin, Procurement Officer, Manager, or Vendor contact).

Future Relationships:
  - User has many VendorContacts (via vendor_id FK)
  - User has many ActivityLogs (via user_id FK)
  - User has many Notifications (via user_id FK)
  - User has many ApprovalRequests as approver (via approver_id FK)
"""

import uuid
from sqlalchemy import Column, String, Boolean, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    # --- Primary Key ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # --- Identity ---
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # --- Role-Based Access Control ---
    # Role options: admin | procurement_officer | vendor | manager
    role = Column(
        SAEnum("admin", "procurement_officer", "vendor", "manager", name="user_role"),
        nullable=False,
        default="vendor",
    )

    # --- Status ---
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # --- Timestamps ---
    # TODO: Add created_at and updated_at columns using a shared TimestampMixin
    # created_at = Column(DateTime(timezone=True), server_default=func.now())
    # updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # --- Future Relationships ---
    # TODO: vendor = relationship("Vendor", back_populates="contacts")
    # TODO: notifications = relationship("Notification", back_populates="user")
    # TODO: activity_logs = relationship("ActivityLog", back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"

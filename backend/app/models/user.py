"""
models/user.py
==============
User and UserSession ORM models.

Tables:
  - users         : All system users across all roles.
  - user_sessions : Refresh token store for secure logout.
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

from app.models.base import Base, TimestampMixin


# ---------------------------------------------------------------------------
# Enum: UserRole
# ---------------------------------------------------------------------------

class UserRole(str, enum.Enum):
    ADMIN               = "admin"
    PROCUREMENT_OFFICER = "procurement_officer"
    VENDOR              = "vendor"
    MANAGER             = "manager"


# ---------------------------------------------------------------------------
# Model: User
# ---------------------------------------------------------------------------

class User(TimestampMixin, Base):
    """
    Represents any system user regardless of role.

    Soft-delete via is_active = False.
    Vendor users carry a vendor_company_id FK to their Vendor record.
    """

    __tablename__ = "users"

    # --- Vendor company link (for role=vendor users only) ---
    vendor_company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # --- Identity ---
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # --- Role ---
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="userrole", create_type=True),
        nullable=False,
        default=UserRole.VENDOR,
    )

    # --- Contact ---
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # --- Status flags ---
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # --- Last login tracking ---
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # --- Relationships ---
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    # vendor_company is set via Vendor.users backref (defined in vendor.py)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"


# ---------------------------------------------------------------------------
# Model: UserSession
# ---------------------------------------------------------------------------

class UserSession(Base):
    """
    Stores refresh tokens for each login session.
    Supports secure server-side logout by revoking the token.
    """

    __tablename__ = "user_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    refresh_token: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<UserSession id={self.id} user_id={self.user_id} revoked={self.is_revoked}>"

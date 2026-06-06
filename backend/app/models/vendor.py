"""
models/vendor.py
================
VendorCategory and Vendor ORM models.

Tables:
  - vendor_categories : Lookup table for vendor business categories.
  - vendors           : Registered vendor/supplier companies.
"""

import uuid
import enum
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DECIMAL,
    Enum as SAEnum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


# ---------------------------------------------------------------------------
# Enum: VendorStatus
# ---------------------------------------------------------------------------

class VendorStatus(str, enum.Enum):
    PENDING     = "pending"
    ACTIVE      = "active"
    SUSPENDED   = "suspended"
    BLACKLISTED = "blacklisted"


# ---------------------------------------------------------------------------
# Model: VendorCategory
# ---------------------------------------------------------------------------

class VendorCategory(TimestampMixin, Base):
    """
    Lookup table for vendor categories (e.g. IT, Logistics, Furniture).
    Soft-deleted via is_active = False.
    """

    __tablename__ = "vendor_categories"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # --- Relationships ---
    vendors: Mapped[list["Vendor"]] = relationship(
        "Vendor", back_populates="category"
    )

    def __repr__(self) -> str:
        return f"<VendorCategory id={self.id} name={self.name}>"


# ---------------------------------------------------------------------------
# Model: Vendor
# ---------------------------------------------------------------------------

class Vendor(TimestampMixin, Base):
    """
    Represents a registered vendor / supplier company.

    Status changes are enforced instead of hard deletes:
      pending → active → suspended / blacklisted

    GST and PAN numbers must be unique across the system.
    """

    __tablename__ = "vendors"

    # --- Business Identity ---
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    gst_number: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True
    )
    pan_number: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True
    )

    # --- Category ---
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendor_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # --- Contact ---
    contact_person: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # --- Address ---
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # --- Ratings & Status ---
    vendor_rating: Mapped[Decimal | None] = mapped_column(
        DECIMAL(3, 2), nullable=True
    )

    status: Mapped[VendorStatus] = mapped_column(
        SAEnum(VendorStatus, name="vendorstatus", create_type=True),
        nullable=False,
        default=VendorStatus.PENDING,
        index=True,
    )

    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Audit: who created this vendor ---
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # --- Relationships ---
    category: Mapped["VendorCategory"] = relationship(
        "VendorCategory", back_populates="vendors"
    )

    # Users linked to this vendor company (role=vendor)
    users: Mapped[list["User"]] = relationship(
        "User",
        foreign_keys="User.vendor_company_id",
        backref="vendor_company",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Vendor id={self.id} company={self.company_name} status={self.status}>"

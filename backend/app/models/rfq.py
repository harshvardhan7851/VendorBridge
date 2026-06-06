"""
models/rfq.py
=============
RFQ (Request for Quotation) and related ORM models.

Tables:
  - rfqs                  : Procurement requests.
  - rfq_line_items        : Individual items within an RFQ.
  - rfq_vendor_assignments: Vendors invited to respond to an RFQ.
  - rfq_attachments       : Supporting documents uploaded to an RFQ.
"""

import uuid
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    DateTime,
    DECIMAL,
    Enum as SAEnum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


# ---------------------------------------------------------------------------
# Enum: RFQStatus
# ---------------------------------------------------------------------------

class RFQStatus(str, enum.Enum):
    DRAFT        = "DRAFT"
    SENT         = "SENT"
    UNDER_REVIEW = "UNDER_REVIEW"
    CLOSED       = "CLOSED"
    CANCELLED    = "CANCELLED"


# ---------------------------------------------------------------------------
# Enum: AssignmentStatus
# ---------------------------------------------------------------------------

class AssignmentStatus(str, enum.Enum):
    INVITED   = "INVITED"
    VIEWED    = "VIEWED"
    SUBMITTED = "SUBMITTED"
    DECLINED  = "DECLINED"


# ---------------------------------------------------------------------------
# Model: RFQ
# ---------------------------------------------------------------------------

class RFQ(TimestampMixin, Base):
    """
    Represents a Request for Quotation issued by a procurement officer.

    Lifecycle: DRAFT → SENT → UNDER_REVIEW → CLOSED / CANCELLED
    """

    __tablename__ = "rfqs"

    # --- Reference Number ---
    rfq_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )

    # --- Details ---
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Status ---
    status: Mapped[RFQStatus] = mapped_column(
        SAEnum(RFQStatus, name="rfqstatus", create_type=True),
        nullable=False,
        default=RFQStatus.DRAFT,
        index=True,
    )

    # --- Deadline ---
    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # --- Audit: who created this RFQ ---
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # --- Relationships ---
    creator: Mapped["User"] = relationship(          # type: ignore[name-defined]
        "User",
        foreign_keys=[created_by],
        lazy="select",
    )

    line_items: Mapped[list["RFQLineItem"]] = relationship(
        "RFQLineItem",
        back_populates="rfq",
        cascade="all, delete-orphan",
        lazy="select",
    )

    vendor_assignments: Mapped[list["RFQVendorAssignment"]] = relationship(
        "RFQVendorAssignment",
        back_populates="rfq",
        cascade="all, delete-orphan",
        lazy="select",
    )

    attachments: Mapped[list["RFQAttachment"]] = relationship(
        "RFQAttachment",
        back_populates="rfq",
        cascade="all, delete-orphan",
        lazy="select",
    )

    quotations: Mapped[list["Quotation"]] = relationship(  # type: ignore[name-defined]
        "Quotation",
        back_populates="rfq",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<RFQ id={self.id} number={self.rfq_number} status={self.status}>"


# ---------------------------------------------------------------------------
# Model: RFQLineItem
# ---------------------------------------------------------------------------

class RFQLineItem(TimestampMixin, Base):
    """
    An individual line item (product / service) within an RFQ.
    Vendors price each line item in their Quotation.
    """

    __tablename__ = "rfq_line_items"

    # --- Foreign Keys ---
    rfq_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rfqs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # --- Item Details ---
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g., "kg", "units"

    # --- Relationships ---
    rfq: Mapped["RFQ"] = relationship("RFQ", back_populates="line_items")

    quotation_line_items: Mapped[list["QuotationLineItem"]] = relationship(  # type: ignore[name-defined]
        "QuotationLineItem",
        back_populates="rfq_line_item",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<RFQLineItem id={self.id} product={self.product_name}>"


# ---------------------------------------------------------------------------
# Model: RFQVendorAssignment
# ---------------------------------------------------------------------------

class RFQVendorAssignment(Base):
    """
    Association between an RFQ and a Vendor (invitation to quote).
    Unique per (rfq_id, vendor_id) pair.
    """

    __tablename__ = "rfq_vendor_assignments"

    __table_args__ = (
        UniqueConstraint("rfq_id", "vendor_id", name="uq_rfq_vendor"),
    )

    # --- Primary Key ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # --- Foreign Keys ---
    rfq_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rfqs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # --- Status ---
    status: Mapped[AssignmentStatus] = mapped_column(
        SAEnum(AssignmentStatus, name="assignmentstatus", create_type=True),
        nullable=False,
        default=AssignmentStatus.INVITED,
        index=True,
    )

    # --- Timestamps ---
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # --- Relationships ---
    rfq: Mapped["RFQ"] = relationship("RFQ", back_populates="vendor_assignments")

    vendor: Mapped["Vendor"] = relationship(  # type: ignore[name-defined]
        "Vendor",
        foreign_keys=[vendor_id],
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<RFQVendorAssignment rfq={self.rfq_id} vendor={self.vendor_id} status={self.status}>"


# ---------------------------------------------------------------------------
# Model: RFQAttachment
# ---------------------------------------------------------------------------

class RFQAttachment(Base):
    """
    File attachments uploaded to an RFQ (e.g., spec sheets, drawings).
    """

    __tablename__ = "rfq_attachments"

    # --- Primary Key ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # --- Foreign Keys ---
    rfq_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rfqs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # --- File Metadata ---
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # --- Timestamps ---
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # --- Relationships ---
    rfq: Mapped["RFQ"] = relationship("RFQ", back_populates="attachments")

    uploader: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User",
        foreign_keys=[uploaded_by],
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<RFQAttachment id={self.id} filename={self.filename}>"

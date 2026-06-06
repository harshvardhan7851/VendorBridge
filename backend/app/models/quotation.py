"""
models/quotation.py
===================
Quotation and QuotationLineItem ORM models.

Tables:
  - quotations            : A vendor's priced response to an RFQ.
  - quotation_line_items  : Per-line-item pricing within a quotation.
"""

import uuid
import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Date,
    DECIMAL,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


# ---------------------------------------------------------------------------
# Enum: QuotationStatus
# ---------------------------------------------------------------------------

class QuotationStatus(str, enum.Enum):
    DRAFT     = "DRAFT"
    SUBMITTED = "SUBMITTED"
    WITHDRAWN = "WITHDRAWN"
    SELECTED  = "SELECTED"
    REJECTED  = "REJECTED"


# ---------------------------------------------------------------------------
# Model: Quotation
# ---------------------------------------------------------------------------

class Quotation(TimestampMixin, Base):
    """
    A vendor's formal price response to an RFQ.

    Lifecycle: DRAFT → SUBMITTED → SELECTED / REJECTED / WITHDRAWN
    """

    __tablename__ = "quotations"

    # --- Reference Number ---
    quotation_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
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
    status: Mapped[QuotationStatus] = mapped_column(
        SAEnum(QuotationStatus, name="quotationstatus", create_type=True),
        nullable=False,
        default=QuotationStatus.DRAFT,
        index=True,
    )

    # --- Validity & Delivery ---
    validity_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # --- Notes & Financials ---
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_amount: Mapped[Decimal | None] = mapped_column(
        DECIMAL(18, 2), nullable=True
    )

    # --- Submission Timestamp ---
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # --- Relationships ---
    rfq: Mapped["RFQ"] = relationship(  # type: ignore[name-defined]
        "RFQ",
        back_populates="quotations",
        lazy="select",
    )

    vendor: Mapped["Vendor"] = relationship(  # type: ignore[name-defined]
        "Vendor",
        foreign_keys=[vendor_id],
        lazy="select",
    )

    line_items: Mapped[list["QuotationLineItem"]] = relationship(
        "QuotationLineItem",
        back_populates="quotation",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Quotation id={self.id} number={self.quotation_number} status={self.status}>"


# ---------------------------------------------------------------------------
# Model: QuotationLineItem
# ---------------------------------------------------------------------------

class QuotationLineItem(Base):
    """
    Vendor's priced response to a single RFQLineItem.
    Stores unit price, quantity, and computed total.
    """

    __tablename__ = "quotation_line_items"

    # --- Primary Key ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # --- Foreign Keys ---
    quotation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quotations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rfq_line_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rfq_line_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # --- Pricing ---
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    total_price: Mapped[Decimal | None] = mapped_column(
        DECIMAL(18, 2), nullable=True
    )  # Denormalised: quantity * unit_price

    # --- Notes ---
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # --- Relationships ---
    quotation: Mapped["Quotation"] = relationship(
        "Quotation", back_populates="line_items"
    )

    rfq_line_item: Mapped["RFQLineItem"] = relationship(  # type: ignore[name-defined]
        "RFQLineItem",
        back_populates="quotation_line_items",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<QuotationLineItem id={self.id} quotation={self.quotation_id} price={self.total_price}>"

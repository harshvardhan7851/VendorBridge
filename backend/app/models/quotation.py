"""
Quotation Models
================
Quotation: A vendor's response to an RFQ.
QuotationLineItem: Individual line items in a quotation.

Future Relationships:
  - Quotation belongs to an RFQ (rfq_id FK)
  - Quotation belongs to a Vendor (vendor_id FK)
  - Quotation has many QuotationLineItems
  - Quotation can generate a PurchaseOrder (one-to-one, if awarded)
"""

import uuid
from sqlalchemy import Column, String, Text, Integer, Numeric, Date, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Quotation(Base):
    __tablename__ = "quotations"

    # --- Primary Key ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # --- Reference Number ---
    quotation_number = Column(String(50), unique=True, nullable=False)  # e.g., QUO-2024-001

    # --- Foreign Keys ---
    # TODO: rfq_id = Column(UUID(as_uuid=True), ForeignKey("rfqs.id"), nullable=False)
    # TODO: vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)

    # --- Financial Summary ---
    subtotal = Column(Numeric(14, 2), nullable=True)
    tax_amount = Column(Numeric(14, 2), nullable=True)
    total_amount = Column(Numeric(14, 2), nullable=True)
    currency = Column(String(10), nullable=False, default="USD")

    # --- Validity ---
    valid_until = Column(Date, nullable=True)

    # --- Status ---
    status = Column(
        SAEnum(
            "draft", "submitted", "under_review", "awarded", "rejected",
            name="quotation_status",
        ),
        nullable=False,
        default="draft",
    )

    # --- Additional ---
    notes = Column(Text, nullable=True)

    # --- Timestamps ---
    # TODO: Add created_at, submitted_at, updated_at

    # --- Future Relationships ---
    # TODO: rfq = relationship("RFQ", back_populates="quotations")
    # TODO: vendor = relationship("Vendor", back_populates="quotations")
    # TODO: line_items = relationship("QuotationLineItem", back_populates="quotation", cascade="all, delete-orphan")
    # TODO: purchase_order = relationship("PurchaseOrder", back_populates="quotation", uselist=False)

    def __repr__(self) -> str:
        return f"<Quotation id={self.id} number={self.quotation_number} status={self.status}>"


class QuotationLineItem(Base):
    __tablename__ = "quotation_line_items"

    # --- Primary Key ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # --- Foreign Keys ---
    # TODO: quotation_id = Column(UUID(as_uuid=True), ForeignKey("quotations.id"), nullable=False)
    # TODO: rfq_line_item_id = Column(UUID(as_uuid=True), ForeignKey("rfq_line_items.id"), nullable=True)

    # --- Item Details ---
    item_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), nullable=True)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total_price = Column(Numeric(14, 2), nullable=True)   # Computed: quantity * unit_price

    # --- Future Relationships ---
    # TODO: quotation = relationship("Quotation", back_populates="line_items")
    # TODO: rfq_line_item = relationship("RFQLineItem", back_populates="quotation_line_items")

    def __repr__(self) -> str:
        return f"<QuotationLineItem id={self.id} item_no={self.item_number}>"

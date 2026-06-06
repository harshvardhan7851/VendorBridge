"""
RFQ (Request for Quotation) Models
====================================
RFQ: A procurement request sent to one or more vendors.
RFQLineItem: Individual line items within an RFQ.

Future Relationships:
  - RFQ belongs to a User (created_by FK)
  - RFQ has many RFQLineItems (one-to-many)
  - RFQ has many Vendors (many-to-many via rfq_vendors)
  - RFQ has many Quotations (one-to-many)
  - RFQ has one ApprovalRequest (one-to-one)
"""

import uuid
from sqlalchemy import Column, String, Text, Integer, Numeric, Date, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class RFQ(Base):
    __tablename__ = "rfqs"

    # --- Primary Key ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # --- Reference Number ---
    rfq_number = Column(String(50), unique=True, nullable=False)   # e.g., RFQ-2024-001

    # --- Details ---
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)

    # --- Dates ---
    submission_deadline = Column(Date, nullable=True)
    delivery_date = Column(Date, nullable=True)

    # --- Status ---
    status = Column(
        SAEnum(
            "draft", "published", "closed", "awarded", "cancelled",
            name="rfq_status",
        ),
        nullable=False,
        default="draft",
    )

    # --- Foreign Keys ---
    # TODO: created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # --- Timestamps ---
    # TODO: Add created_at, updated_at

    # --- Future Relationships ---
    # TODO: created_by_user = relationship("User", back_populates="rfqs")
    # TODO: line_items = relationship("RFQLineItem", back_populates="rfq", cascade="all, delete-orphan")
    # TODO: vendors = relationship("Vendor", secondary="rfq_vendors", back_populates="rfqs")
    # TODO: quotations = relationship("Quotation", back_populates="rfq")
    # TODO: approval = relationship("ApprovalRequest", back_populates="rfq", uselist=False)

    def __repr__(self) -> str:
        return f"<RFQ id={self.id} number={self.rfq_number} status={self.status}>"


class RFQLineItem(Base):
    __tablename__ = "rfq_line_items"

    # --- Primary Key ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # --- Foreign Keys ---
    # TODO: rfq_id = Column(UUID(as_uuid=True), ForeignKey("rfqs.id"), nullable=False)

    # --- Item Details ---
    item_number = Column(Integer, nullable=False)        # Line item sequence
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), nullable=True)             # e.g., "units", "kg", "hours"
    estimated_unit_price = Column(Numeric(12, 2), nullable=True)

    # --- Future Relationships ---
    # TODO: rfq = relationship("RFQ", back_populates="line_items")
    # TODO: quotation_line_items = relationship("QuotationLineItem", back_populates="rfq_line_item")

    def __repr__(self) -> str:
        return f"<RFQLineItem id={self.id} item_no={self.item_number}>"

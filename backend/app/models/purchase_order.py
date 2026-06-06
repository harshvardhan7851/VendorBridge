"""
Purchase Order Models
======================
PurchaseOrder: A formal order sent to a vendor after quotation is awarded.
POLineItem: Individual line items within a purchase order.

Future Relationships:
  - PurchaseOrder belongs to a Quotation (quotation_id FK)
  - PurchaseOrder belongs to a Vendor (vendor_id FK)
  - PurchaseOrder has many POLineItems
  - PurchaseOrder has one ApprovalRequest
  - PurchaseOrder has many Invoices
"""

import uuid
from sqlalchemy import Column, String, Text, Integer, Numeric, Date, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    # --- Primary Key ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # --- Reference Number ---
    po_number = Column(String(50), unique=True, nullable=False)  # e.g., PO-2024-001

    # --- Foreign Keys ---
    # TODO: quotation_id = Column(UUID(as_uuid=True), ForeignKey("quotations.id"), nullable=True)
    # TODO: vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)
    # TODO: created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # --- Financial ---
    subtotal = Column(Numeric(14, 2), nullable=True)
    tax_amount = Column(Numeric(14, 2), nullable=True)
    total_amount = Column(Numeric(14, 2), nullable=True)
    currency = Column(String(10), nullable=False, default="USD")

    # --- Dates ---
    order_date = Column(Date, nullable=True)
    expected_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)

    # --- Status ---
    status = Column(
        SAEnum(
            "draft", "pending_approval", "approved", "sent", "acknowledged",
            "partially_delivered", "delivered", "closed", "cancelled",
            name="po_status",
        ),
        nullable=False,
        default="draft",
    )

    # --- Additional ---
    delivery_address = Column(Text, nullable=True)
    terms_and_conditions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # --- Future Relationships ---
    # TODO: quotation = relationship("Quotation", back_populates="purchase_order")
    # TODO: vendor = relationship("Vendor", back_populates="purchase_orders")
    # TODO: line_items = relationship("POLineItem", back_populates="purchase_order", cascade="all, delete-orphan")
    # TODO: invoices = relationship("Invoice", back_populates="purchase_order")
    # TODO: approval = relationship("ApprovalRequest", back_populates="purchase_order", uselist=False)

    def __repr__(self) -> str:
        return f"<PurchaseOrder id={self.id} number={self.po_number} status={self.status}>"


class POLineItem(Base):
    __tablename__ = "po_line_items"

    # --- Primary Key ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # --- Foreign Keys ---
    # TODO: purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False)

    # --- Item Details ---
    item_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), nullable=True)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total_price = Column(Numeric(14, 2), nullable=True)

    # --- Delivery Tracking ---
    quantity_received = Column(Numeric(10, 2), nullable=True, default=0)

    # --- Future Relationships ---
    # TODO: purchase_order = relationship("PurchaseOrder", back_populates="line_items")

    def __repr__(self) -> str:
        return f"<POLineItem id={self.id} item_no={self.item_number}>"

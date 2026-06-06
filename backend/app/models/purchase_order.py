"""
models/purchase_order.py
========================
Purchase Order models for Module 3.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey, String, Date, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

class PurchaseOrder(TimestampMixin, Base):
    __tablename__ = "purchase_orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    po_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    approval_request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("approval_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    rfq_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False, index=True)
    quotation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    subtotal: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    cgst: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, default=0)
    sgst: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, default=0)
    igst: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, default=0)
    grand_total: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT", index=True)
    issued_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    line_items: Mapped[list["POLineItem"]] = relationship("POLineItem", back_populates="purchase_order", cascade="all, delete-orphan")


class POLineItem(Base):
    __tablename__ = "po_line_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    purchase_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    quantity: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="line_items")

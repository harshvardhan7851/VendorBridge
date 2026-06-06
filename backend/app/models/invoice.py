"""
models/invoice.py
=================
Invoice models for Module 3.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey, String, Date, Text, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Invoice(TimestampMixin, Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    invoice_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    purchase_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False, index=True)

    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    subtotal: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    grand_total: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT", index=True)
    
    pdf_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    line_items: Mapped[list["InvoiceLineItem"]] = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    invoice_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    quantity: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="line_items")

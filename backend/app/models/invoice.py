"""
Invoice Model
=============
Represents a vendor invoice submitted against a Purchase Order.
"""

import uuid
from sqlalchemy import Column, String, Text, Numeric, Date
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String(50), unique=True, nullable=False)
    internal_reference = Column(String(50), nullable=True)

    # TODO: purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"))
    # TODO: vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"))

    subtotal = Column(Numeric(14, 2), nullable=True)
    tax_amount = Column(Numeric(14, 2), nullable=True)
    total_amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="USD")
    amount_paid = Column(Numeric(14, 2), nullable=True, default=0)

    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    payment_date = Column(Date, nullable=True)

    status = Column(
        SAEnum(
            "received", "under_review", "approved", "rejected",
            "payment_pending", "paid", "partially_paid",
            name="invoice_status",
        ),
        nullable=False,
        default="received",
    )

    description = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # TODO: purchase_order = relationship("PurchaseOrder", back_populates="invoices")
    # TODO: vendor = relationship("Vendor", back_populates="invoices")

    def __repr__(self) -> str:
        return f"<Invoice id={self.id} number={self.invoice_number} status={self.status}>"

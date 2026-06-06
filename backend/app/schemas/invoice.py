"""
Invoice Schemas — Pydantic v2 placeholders.
"""
from uuid import UUID
from typing import Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class InvoiceCreate(BaseModel):
    purchase_order_id: UUID
    invoice_number: str
    invoice_date: date
    due_date: Optional[date] = None
    total_amount: Decimal
    currency: str = "USD"
    description: Optional[str] = None


class InvoiceUpdate(BaseModel):
    status: Optional[str] = None
    payment_date: Optional[date] = None
    amount_paid: Optional[Decimal] = None
    rejection_reason: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: UUID
    invoice_number: str
    status: str
    total_amount: Decimal
    amount_paid: Optional[Decimal] = None
    currency: str
    invoice_date: date
    due_date: Optional[date] = None
    payment_date: Optional[date] = None

    model_config = {"from_attributes": True}

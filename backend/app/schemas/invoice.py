"""
schemas/invoice.py
"""
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
import uuid
from datetime import datetime, date
from app.enums.module3 import InvoiceStatus

class InvoiceLineItemResponse(BaseModel):
    id: uuid.UUID
    description: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    model_config = ConfigDict(from_attributes=True)

class InvoiceStatusUpdate(BaseModel):
    status: InvoiceStatus

class InvoiceResponse(BaseModel):
    id: uuid.UUID
    invoice_number: str
    purchase_order_id: uuid.UUID
    vendor_id: uuid.UUID
    invoice_date: date
    subtotal: Decimal
    tax_amount: Decimal
    grand_total: Decimal
    status: str
    pdf_url: str | None
    email_sent: bool
    created_at: datetime
    line_items: list[InvoiceLineItemResponse] = []
    model_config = ConfigDict(from_attributes=True)

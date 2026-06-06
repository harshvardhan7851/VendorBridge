"""
schemas/purchase_order.py
"""
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
import uuid
from datetime import datetime, date
from app.enums.module3 import POStatus

class POLineItemResponse(BaseModel):
    id: uuid.UUID
    product_name: str
    description: str | None
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    model_config = ConfigDict(from_attributes=True)

class POStatusUpdate(BaseModel):
    status: POStatus

class POResponse(BaseModel):
    id: uuid.UUID
    po_number: str
    approval_request_id: uuid.UUID
    vendor_id: uuid.UUID
    rfq_id: uuid.UUID
    quotation_id: uuid.UUID
    subtotal: Decimal
    cgst: Decimal
    sgst: Decimal
    igst: Decimal
    grand_total: Decimal
    status: str
    issued_date: date | None
    created_by: uuid.UUID | None
    created_at: datetime
    line_items: list[POLineItemResponse] = []
    model_config = ConfigDict(from_attributes=True)

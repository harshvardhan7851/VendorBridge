"""
schemas/quotation.py
====================
Pydantic v2 schemas for Quotation and QuotationLineItem models.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from app.models.quotation import QuotationStatus


# ===========================================================================
# QuotationLineItem
# ===========================================================================

class QuotationLineItemCreate(BaseModel):
    rfq_line_item_id: uuid.UUID
    unit_price: Decimal = Field(..., ge=0, description="Unit price for the item")
    quantity: Decimal = Field(..., gt=0, description="Quantity offered")
    notes: str | None = None

class QuotationLineItemUpdate(BaseModel):
    unit_price: Decimal | None = Field(default=None, ge=0)
    quantity: Decimal | None = Field(default=None, gt=0)
    notes: str | None = None

class QuotationLineItemResponse(BaseModel):
    id: uuid.UUID
    quotation_id: uuid.UUID
    rfq_line_item_id: uuid.UUID | None
    unit_price: Decimal
    quantity: Decimal
    total_price: Decimal | None
    notes: str | None
    created_at: datetime
    
    # Extra field for comparison engine
    is_lowest_price: bool | None = None

    model_config = {"from_attributes": True}


# ===========================================================================
# Quotation
# ===========================================================================

class QuotationCreate(BaseModel):
    rfq_id: uuid.UUID
    validity_date: date | None = None
    delivery_days: int | None = Field(default=None, ge=0)
    notes: str | None = None
    line_items: list[QuotationLineItemCreate] = Field(..., min_length=1)

class QuotationUpdate(BaseModel):
    validity_date: date | None = None
    delivery_days: int | None = Field(default=None, ge=0)
    notes: str | None = None

class QuotationResponse(BaseModel):
    id: uuid.UUID
    quotation_number: str
    rfq_id: uuid.UUID
    vendor_id: uuid.UUID
    status: QuotationStatus
    validity_date: date | None
    delivery_days: int | None
    notes: str | None
    total_amount: Decimal | None
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class QuotationDetail(QuotationResponse):
    line_items: list[QuotationLineItemResponse] = []
    
    # Extra field for comparison engine
    is_lowest_total: bool | None = None
    vendor_name: str | None = None

    model_config = {"from_attributes": True}

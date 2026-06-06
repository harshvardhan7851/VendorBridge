"""
Quotation Schemas
=================
Pydantic v2 schemas for Quotation and QuotationLineItem models.
"""

from uuid import UUID
from typing import Optional, List
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field


class QuotationLineItemCreate(BaseModel):
    item_number: int
    description: str
    quantity: float = Field(..., gt=0)
    unit: Optional[str] = None
    unit_price: Decimal = Field(..., gt=0)


class QuotationLineItemResponse(BaseModel):
    id: UUID
    item_number: int
    description: str
    quantity: float
    unit: Optional[str] = None
    unit_price: Decimal
    total_price: Optional[Decimal] = None

    model_config = {"from_attributes": True}


class QuotationCreate(BaseModel):
    rfq_id: UUID
    valid_until: Optional[date] = None
    currency: str = "USD"
    notes: Optional[str] = None
    line_items: List[QuotationLineItemCreate] = Field(default_factory=list)


class QuotationUpdate(BaseModel):
    valid_until: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class QuotationResponse(BaseModel):
    id: UUID
    quotation_number: str
    status: str
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    currency: str
    valid_until: Optional[date] = None
    notes: Optional[str] = None
    line_items: List[QuotationLineItemResponse] = []

    model_config = {"from_attributes": True}

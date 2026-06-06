"""
Purchase Order Schemas — Pydantic v2 placeholders.
"""
from uuid import UUID
from typing import Optional, List
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field


class POLineItemCreate(BaseModel):
    item_number: int
    description: str
    quantity: float = Field(..., gt=0)
    unit: Optional[str] = None
    unit_price: Decimal = Field(..., gt=0)


class POLineItemResponse(BaseModel):
    id: UUID
    item_number: int
    description: str
    quantity: float
    unit_price: Decimal
    total_price: Optional[Decimal] = None
    quantity_received: Optional[float] = None

    model_config = {"from_attributes": True}


class PurchaseOrderCreate(BaseModel):
    vendor_id: UUID
    quotation_id: Optional[UUID] = None
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    delivery_address: Optional[str] = None
    currency: str = "USD"
    notes: Optional[str] = None
    line_items: List[POLineItemCreate] = Field(default_factory=list)


class PurchaseOrderUpdate(BaseModel):
    status: Optional[str] = None
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    notes: Optional[str] = None


class PurchaseOrderResponse(BaseModel):
    id: UUID
    po_number: str
    status: str
    total_amount: Optional[Decimal] = None
    currency: str
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    line_items: List[POLineItemResponse] = []

    model_config = {"from_attributes": True}

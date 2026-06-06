"""
RFQ Schemas
===========
Pydantic v2 schemas for RFQ and RFQLineItem models.
"""

from uuid import UUID
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field


class RFQLineItemCreate(BaseModel):
    item_number: int
    description: str
    quantity: float = Field(..., gt=0)
    unit: Optional[str] = None
    estimated_unit_price: Optional[float] = None


class RFQLineItemResponse(BaseModel):
    id: UUID
    item_number: int
    description: str
    quantity: float
    unit: Optional[str] = None
    estimated_unit_price: Optional[float] = None

    model_config = {"from_attributes": True}


class RFQCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    submission_deadline: Optional[date] = None
    delivery_date: Optional[date] = None
    line_items: List[RFQLineItemCreate] = Field(default_factory=list)


class RFQUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    submission_deadline: Optional[date] = None
    delivery_date: Optional[date] = None
    status: Optional[str] = None


class RFQResponse(BaseModel):
    id: UUID
    rfq_number: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    submission_deadline: Optional[date] = None
    delivery_date: Optional[date] = None
    status: str
    line_items: List[RFQLineItemResponse] = []

    model_config = {"from_attributes": True}

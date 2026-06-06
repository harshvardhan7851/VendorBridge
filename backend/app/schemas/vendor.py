"""
Vendor Schemas
==============
Pydantic v2 schemas for Vendor model.
"""

from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class VendorCreate(BaseModel):
    """Schema for registering a new vendor."""
    company_name: str = Field(..., min_length=2, max_length=255)
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None


class VendorUpdate(BaseModel):
    """Schema for updating vendor information. All fields optional."""
    company_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class VendorResponse(BaseModel):
    """Schema returned in API responses."""
    id: UUID
    company_name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    status: str
    is_active: bool

    model_config = {"from_attributes": True}

"""
schemas/vendor.py
=================
Pydantic v2 schemas for Vendor Category and Vendor endpoints.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field
from app.models.vendor import VendorStatus


# ===========================================================================
# Vendor Category
# ===========================================================================

class VendorCategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None


class VendorCategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    is_active: bool | None = None


class VendorCategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# Vendor
# ===========================================================================

class VendorCreate(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255)
    gst_number: str | None = Field(default=None, max_length=50)
    pan_number: str | None = Field(default=None, max_length=50)
    category_id: uuid.UUID | None = None
    contact_person: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    website: str | None = Field(default=None, max_length=255)
    address: str | None = None
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    remarks: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "company_name": "Acme Supplies Ltd.",
                "gst_number": "27AAPFU0939F1ZV",
                "pan_number": "AAPFU0939F",
                "email": "contact@acme.com",
                "city": "Mumbai",
                "country": "India",
            }
        }
    }


class VendorUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=2, max_length=255)
    gst_number: str | None = Field(default=None, max_length=50)
    pan_number: str | None = Field(default=None, max_length=50)
    category_id: uuid.UUID | None = None
    contact_person: str | None = None
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    website: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    vendor_rating: Decimal | None = Field(default=None, ge=0, le=5)
    remarks: str | None = None


class VendorStatusUpdate(BaseModel):
    status: VendorStatus
    remarks: str | None = None


class VendorResponse(BaseModel):
    id: uuid.UUID
    company_name: str
    gst_number: str | None
    pan_number: str | None
    category_id: uuid.UUID | None
    category: VendorCategoryResponse | None = None
    contact_person: str | None
    email: str | None
    phone: str | None
    website: str | None
    address: str | None
    city: str | None
    state: str | None
    country: str | None
    postal_code: str | None
    vendor_rating: Decimal | None
    status: VendorStatus
    remarks: str | None
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Filter query params model
class VendorFilterParams(BaseModel):
    search: str | None = None
    status: VendorStatus | None = None
    category_id: uuid.UUID | None = None
    sort_by: str = Field(default="created_at", pattern="^(company_name|created_at)$")
    sort_dir: str = Field(default="desc", pattern="^(asc|desc)$")

"""
schemas/user.py
===============
Pydantic v2 schemas for User management endpoints.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)
    role: UserRole = UserRole.VENDOR
    phone: str | None = Field(default=None, max_length=20)
    vendor_company_id: uuid.UUID | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "officer@vendorbridge.com",
                "password": "Pass@1234",
                "full_name": "Ravi Sharma",
                "role": "procurement_officer",
            }
        }
    }


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    role: UserRole | None = None
    vendor_company_id: uuid.UUID | None = None


# ---------------------------------------------------------------------------
# Status patch
# ---------------------------------------------------------------------------

class UserStatusUpdate(BaseModel):
    is_active: bool


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    phone: str | None
    is_active: bool
    is_verified: bool
    vendor_company_id: uuid.UUID | None
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

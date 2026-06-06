"""
User Schemas
============
Pydantic v2 schemas for User model.
  - UserCreate   : Request body for user registration
  - UserUpdate   : Request body for updating a user
  - UserResponse : Response model returned to clients
"""

from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, description="Plain text password — will be hashed")
    role: str = Field(default="vendor", description="One of: admin, procurement_officer, vendor, manager")

    model_config = {"json_schema_extra": {"example": {
        "email": "john.doe@example.com",
        "full_name": "John Doe",
        "password": "SecurePass123!",
        "role": "procurement_officer",
    }}}


class UserUpdate(BaseModel):
    """Schema for partially updating a user. All fields optional."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema returned in API responses. Excludes sensitive fields."""
    id: UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for JWT authentication responses."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

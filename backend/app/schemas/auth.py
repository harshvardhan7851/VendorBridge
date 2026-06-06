"""
schemas/auth.py
===============
Request and response schemas for the auth endpoints.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "admin@vendorbridge.com",
                "password": "Admin@123",
            }
        }
    }


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Min 8 chars")
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=20)

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "Secure@123",
                "full_name": "Jane Doe",
                "phone": "+91-9999999999",
            }
        }
    }


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ApiResponse(BaseModel):
    """Standard API envelope used by all endpoints."""
    success: bool = True
    message: str = ""
    data: dict | list | None = None

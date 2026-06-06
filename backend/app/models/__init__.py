"""
models/__init__.py
==================
Register all models so Alembic autogenerate picks them up.
Import order matters: Base models before models with FKs.
"""

from app.models.base import Base  # noqa: F401
from app.models.vendor import VendorCategory, Vendor, VendorStatus  # noqa: F401
from app.models.user import User, UserSession, UserRole  # noqa: F401

__all__ = [
    "Base",
    "VendorCategory",
    "Vendor",
    "VendorStatus",
    "User",
    "UserSession",
    "UserRole",
]

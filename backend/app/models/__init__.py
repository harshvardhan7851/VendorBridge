"""
models/__init__.py
==================
Register all models so Alembic autogenerate picks them up.
Import order matters: Base models before models with FKs.

Module 1: User, Vendor, VendorCategory
Module 2: RFQ, RFQLineItem, RFQVendorAssignment, RFQAttachment,
          Quotation, QuotationLineItem, Notification
"""

from app.models.base import Base  # noqa: F401

# --- Module 1 ---
from app.models.vendor import VendorCategory, Vendor, VendorStatus  # noqa: F401
from app.models.user import User, UserSession, UserRole  # noqa: F401

# --- Module 2: RFQ cluster ---
from app.models.rfq import (  # noqa: F401
    RFQ,
    RFQLineItem,
    RFQVendorAssignment,
    RFQAttachment,
    RFQStatus,
    AssignmentStatus,
)

# --- Module 2: Quotation cluster ---
from app.models.quotation import (  # noqa: F401
    Quotation,
    QuotationLineItem,
    QuotationStatus,
)

# --- Module 2: Notification ---
from app.models.notification import Notification, NotificationType  # noqa: F401

# --- Module 3: Approval ---
from app.models.approval import ApprovalTrigger  # noqa: F401

__all__ = [
    # Base
    "Base",
    # Module 1
    "VendorCategory",
    "Vendor",
    "VendorStatus",
    "User",
    "UserSession",
    "UserRole",
    # Module 2 — RFQ
    "RFQ",
    "RFQLineItem",
    "RFQVendorAssignment",
    "RFQAttachment",
    "RFQStatus",
    "AssignmentStatus",
    # Module 2 — Quotation
    "Quotation",
    "QuotationLineItem",
    "QuotationStatus",
    # Module 2 — Notification
    "Notification",
    "NotificationType",
    # Module 3 - Approval
    "ApprovalTrigger",
]

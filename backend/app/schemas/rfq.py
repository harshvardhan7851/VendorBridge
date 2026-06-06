"""
schemas/rfq.py
==============
Pydantic v2 schemas for RFQ, RFQLineItem, RFQVendorAssignment,
RFQAttachment and related request/response shapes.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field

from app.models.rfq import AssignmentStatus, RFQStatus


# ===========================================================================
# RFQLineItem
# ===========================================================================

class RFQLineItemCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    quantity: Decimal = Field(..., gt=0)
    unit: str | None = Field(default=None, max_length=50)

    model_config = {
        "json_schema_extra": {
            "example": {
                "product_name": "A4 Paper Ream",
                "quantity": "50.00",
                "unit": "reams",
            }
        }
    }


class RFQLineItemUpdate(BaseModel):
    product_name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    quantity: Decimal | None = Field(default=None, gt=0)
    unit: str | None = Field(default=None, max_length=50)


class RFQLineItemResponse(BaseModel):
    id: uuid.UUID
    rfq_id: uuid.UUID
    product_name: str
    description: str | None
    quantity: Decimal
    unit: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# RFQ
# ===========================================================================

class RFQCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str | None = None
    deadline: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Office Stationery Q1 2025",
                "description": "Bulk stationery purchase for all departments.",
                "deadline": "2025-09-30T17:00:00Z",
            }
        }
    }


class RFQUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=255)
    description: str | None = None
    deadline: datetime | None = None


# ===========================================================================
# RFQVendorAssignment
# ===========================================================================

class AssignVendorsRequest(BaseModel):
    vendor_ids: list[uuid.UUID] = Field(..., min_length=1)

    model_config = {
        "json_schema_extra": {
            "example": {"vendor_ids": ["<uuid1>", "<uuid2>"]}
        }
    }


class RFQVendorAssignmentResponse(BaseModel):
    id: uuid.UUID
    rfq_id: uuid.UUID
    vendor_id: uuid.UUID
    vendor_name: str | None = None   # populated in service
    status: AssignmentStatus
    invited_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# RFQAttachment
# ===========================================================================

class RFQAttachmentResponse(BaseModel):
    id: uuid.UUID
    rfq_id: uuid.UUID
    filename: str
    file_path: str
    file_size: int | None
    uploaded_by: uuid.UUID | None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# RFQ Response (list vs. detail)
# ===========================================================================

class RFQListItem(BaseModel):
    """Lightweight shape returned in paginated list — no nested collections."""
    id: uuid.UUID
    rfq_number: str
    title: str
    description: str | None
    status: RFQStatus
    deadline: datetime | None
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RFQDetail(BaseModel):
    """Full detail shape — includes nested line_items, vendors, attachments."""
    id: uuid.UUID
    rfq_number: str
    title: str
    description: str | None
    status: RFQStatus
    deadline: datetime | None
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    line_items: list[RFQLineItemResponse] = []
    assigned_vendors: list[RFQVendorAssignmentResponse] = []
    attachments: list[RFQAttachmentResponse] = []

    model_config = {"from_attributes": True}

"""
Approval Schemas — Pydantic v2 placeholders.
"""
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class ApprovalCreate(BaseModel):
    approval_type: str
    rfq_id: Optional[UUID] = None
    purchase_order_id: Optional[UUID] = None
    requester_notes: Optional[str] = None


class ApprovalUpdate(BaseModel):
    status: Optional[str] = None
    approver_comments: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: UUID
    approval_number: str
    approval_type: str
    status: str
    requester_notes: Optional[str] = None
    approver_comments: Optional[str] = None

    model_config = {"from_attributes": True}

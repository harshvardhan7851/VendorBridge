"""
schemas/approval.py
"""
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
import uuid
from datetime import datetime
from app.enums.module3 import ApprovalStatus

class ApprovalCreate(BaseModel):
    rfq_id: uuid.UUID
    quotation_id: uuid.UUID
    vendor_id: uuid.UUID
    amount: Decimal

class ApprovalDecisionRequest(BaseModel):
    remarks: str

class ApprovalHistoryResponse(BaseModel):
    id: uuid.UUID
    action: str
    performed_by: uuid.UUID
    remarks: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ApprovalResponse(BaseModel):
    id: uuid.UUID
    rfq_id: uuid.UUID
    quotation_id: uuid.UUID
    vendor_id: uuid.UUID
    requested_by: uuid.UUID
    approved_by: uuid.UUID | None
    amount: Decimal
    status: str
    remarks: str | None
    requested_at: datetime
    decision_at: datetime | None
    history: list[ApprovalHistoryResponse] = []
    model_config = ConfigDict(from_attributes=True)

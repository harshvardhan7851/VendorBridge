"""
ApprovalRequest Model
======================
Tracks approval/rejection workflow for RFQs and Purchase Orders.

Future Relationships:
  - ApprovalRequest belongs to an RFQ (optional, rfq_id FK)
  - ApprovalRequest belongs to a PurchaseOrder (optional, po_id FK)
  - ApprovalRequest belongs to an approver User (approver_id FK)
  - ApprovalRequest belongs to a requester User (requester_id FK)
"""

import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    # --- Primary Key ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # --- Reference Number ---
    approval_number = Column(String(50), unique=True, nullable=False)  # e.g., APR-2024-001

    # --- Approval Type ---
    approval_type = Column(
        SAEnum("rfq", "purchase_order", "vendor_registration", name="approval_type"),
        nullable=False,
    )

    # --- Status ---
    status = Column(
        SAEnum("pending", "approved", "rejected", "escalated", name="approval_status"),
        nullable=False,
        default="pending",
    )

    # --- Comments ---
    requester_notes = Column(Text, nullable=True)
    approver_comments = Column(Text, nullable=True)

    # --- Foreign Keys ---
    # TODO: rfq_id = Column(UUID(as_uuid=True), ForeignKey("rfqs.id"), nullable=True)
    # TODO: purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=True)
    # TODO: requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    # TODO: approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # --- Timestamps ---
    # TODO: Add created_at, responded_at

    # --- Future Relationships ---
    # TODO: rfq = relationship("RFQ", back_populates="approval")
    # TODO: purchase_order = relationship("PurchaseOrder", back_populates="approval")
    # TODO: requester = relationship("User", foreign_keys=[requester_id])
    # TODO: approver = relationship("User", foreign_keys=[approver_id])

    def __repr__(self) -> str:
        return f"<ApprovalRequest id={self.id} type={self.approval_type} status={self.status}>"

"""
ApprovalTrigger Model
=====================
Tracks when a quotation is selected as the winner. Module 3 will consume these
to orchestrate multi-step approval workflows before PO generation.
"""

import uuid
from decimal import Decimal
from sqlalchemy import DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

class ApprovalTrigger(TimestampMixin, Base):
    __tablename__ = "approval_triggers"

    # --- Foreign Keys ---
    rfq_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quotation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # --- Financial ---
    amount: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)

    def __repr__(self) -> str:
        return f"<ApprovalTrigger id={self.id} rfq={self.rfq_id} quotation={self.quotation_id} amount={self.amount}>"

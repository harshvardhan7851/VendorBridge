"""
services/approval_service.py
============================
Business logic for Approval Workflows.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.enums.module3 import ApprovalStatus, ApprovalAction
from app.models.approval import ApprovalTrigger, ApprovalRequest, ApprovalHistory
from app.models.user import User
from app.schemas.approval import ApprovalCreate, ApprovalDecisionRequest
from app.services.activity_log_service import log_activity


class ApprovalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_approval_request(
        self, payload: ApprovalCreate, requested_by_user_id: uuid.UUID
    ) -> ApprovalRequest:
        
        # Validate that the trigger exists
        trigger_query = await self.db.execute(
            select(ApprovalTrigger).where(
                ApprovalTrigger.rfq_id == payload.rfq_id,
                ApprovalTrigger.quotation_id == payload.quotation_id
            )
        )
        trigger = trigger_query.scalar_one_or_none()
        if not trigger:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval trigger not found for this RFQ and Quotation."
            )

        # Check if approval request already exists for this RFQ
        existing_query = await self.db.execute(
            select(ApprovalRequest).where(ApprovalRequest.rfq_id == payload.rfq_id)
        )
        if existing_query.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An approval request already exists for this RFQ."
            )

        # Create Request
        approval_request = ApprovalRequest(
            rfq_id=payload.rfq_id,
            quotation_id=payload.quotation_id,
            vendor_id=payload.vendor_id,
            requested_by=requested_by_user_id,
            amount=payload.amount,
            status=ApprovalStatus.PENDING,
        )
        self.db.add(approval_request)
        await self.db.flush()

        # Create History
        history = ApprovalHistory(
            approval_request_id=approval_request.id,
            action=ApprovalAction.CREATED,
            performed_by=requested_by_user_id,
            remarks="Approval request initiated."
        )
        self.db.add(history)

        # Log Activity
        await log_activity(
            self.db,
            user_id=requested_by_user_id,
            action="APPROVAL_CREATED",
            entity_type="approval_request",
            entity_id=approval_request.id,
            new_values={"status": ApprovalStatus.PENDING.value}
        )
        
        # Optional: delete the trigger if it's considered consumed
        await self.db.delete(trigger)
        await self.db.commit()
        await self.db.refresh(approval_request)
        
        return approval_request

    async def _get_approval_or_404(self, approval_id: uuid.UUID) -> ApprovalRequest:
        query = select(ApprovalRequest).options(selectinload(ApprovalRequest.history)).where(ApprovalRequest.id == approval_id)
        result = await self.db.execute(query)
        approval = result.scalar_one_or_none()
        if not approval:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found.")
        return approval

    async def approve_request(
        self, approval_id: uuid.UUID, manager_user_id: uuid.UUID, payload: ApprovalDecisionRequest
    ) -> ApprovalRequest:
        approval = await self._get_approval_or_404(approval_id)
        
        if approval.status != ApprovalStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Approval request is not PENDING.")
            
        approval.status = ApprovalStatus.APPROVED
        approval.decision_at = datetime.now(timezone.utc)
        approval.approved_by = manager_user_id
        
        history = ApprovalHistory(
            approval_request_id=approval.id,
            action=ApprovalAction.APPROVED,
            performed_by=manager_user_id,
            remarks=payload.remarks
        )
        self.db.add(history)
        
        await log_activity(
            self.db,
            user_id=manager_user_id,
            action="APPROVAL_APPROVED",
            entity_type="approval_request",
            entity_id=approval.id,
            old_values={"status": ApprovalStatus.PENDING.value},
            new_values={"status": ApprovalStatus.APPROVED.value}
        )
        
        await self.db.commit()
        await self.db.refresh(approval)
        return approval

    async def reject_request(
        self, approval_id: uuid.UUID, manager_user_id: uuid.UUID, payload: ApprovalDecisionRequest
    ) -> ApprovalRequest:
        approval = await self._get_approval_or_404(approval_id)
        
        if approval.status != ApprovalStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Approval request is not PENDING.")
            
        approval.status = ApprovalStatus.REJECTED
        approval.decision_at = datetime.now(timezone.utc)
        
        history = ApprovalHistory(
            approval_request_id=approval.id,
            action=ApprovalAction.REJECTED,
            performed_by=manager_user_id,
            remarks=payload.remarks
        )
        self.db.add(history)
        
        await log_activity(
            self.db,
            user_id=manager_user_id,
            action="APPROVAL_REJECTED",
            entity_type="approval_request",
            entity_id=approval.id,
            old_values={"status": ApprovalStatus.PENDING.value},
            new_values={"status": ApprovalStatus.REJECTED.value}
        )
        
        await self.db.commit()
        await self.db.refresh(approval)
        return approval

    async def list_approvals(
        self, user: User, status_filter: str | None = None, date_filter: str | None = None, min_amount: float | None = None, max_amount: float | None = None, page: int = 1, size: int = 20
    ) -> tuple[list[ApprovalRequest], int]:
        query = select(ApprovalRequest)
        
        if status_filter:
            query = query.where(ApprovalRequest.status == status_filter)
        if date_filter:
            # basic string match assumption, ideally parsed to dates
            pass 
        if min_amount is not None:
            query = query.where(ApprovalRequest.amount >= Decimal(str(min_amount)))
        if max_amount is not None:
            query = query.where(ApprovalRequest.amount <= Decimal(str(max_amount)))
            
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()
        
        offset = (page - 1) * size
        query = query.order_by(ApprovalRequest.created_at.desc()).offset(offset).limit(size).options(selectinload(ApprovalRequest.history))
        
        result = await self.db.execute(query)
        approvals = list(result.scalars().all())
        return approvals, total

    async def get_approval_detail(self, approval_id: uuid.UUID) -> ApprovalRequest:
        return await self._get_approval_or_404(approval_id)

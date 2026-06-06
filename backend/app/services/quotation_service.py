"""
services/quotation_service.py
=============================
Business logic for Quotation management and winner selection.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.notification import Notification, NotificationType
from app.models.quotation import Quotation, QuotationLineItem, QuotationStatus
from app.models.rfq import RFQ, RFQStatus, RFQVendorAssignment, AssignmentStatus
from app.models.user import User, UserRole
from app.models.approval import ApprovalTrigger
from app.schemas.quotation import QuotationCreate, QuotationUpdate


from app.utils.reference_generator import generate_quotation_number


class QuotationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_quotation(self, quotation_id: uuid.UUID) -> Quotation:
        result = await self.db.execute(
            select(Quotation)
            .options(
                selectinload(Quotation.line_items),
                selectinload(Quotation.rfq),
                selectinload(Quotation.vendor)
            )
            .where(Quotation.id == quotation_id)
        )
        q = result.scalar_one_or_none()
        if not q:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quotation '{quotation_id}' not found.",
            )
        return q

    async def create_quotation(self, payload: QuotationCreate, current_user: User) -> Quotation:
        if current_user.vendor_company_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not associated with a vendor.")

        # Check vendor assignment status
        assign_result = await self.db.execute(
            select(RFQVendorAssignment)
            .where(RFQVendorAssignment.rfq_id == payload.rfq_id)
            .where(RFQVendorAssignment.vendor_id == current_user.vendor_company_id)
        )
        assignment = assign_result.scalar_one_or_none()

        if not assignment or assignment.status not in (AssignmentStatus.INVITED, AssignmentStatus.VIEWED):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not eligible to create a quotation for this RFQ.",
            )

        # Check if draft already exists
        existing_draft = await self.db.execute(
            select(Quotation)
            .where(Quotation.rfq_id == payload.rfq_id)
            .where(Quotation.vendor_id == current_user.vendor_company_id)
            .where(Quotation.status == QuotationStatus.DRAFT)
        )
        if existing_draft.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A draft quotation already exists for this RFQ.",
            )

        total_amount = Decimal("0.00")
        line_items = []
        for li in payload.line_items:
            tp = li.unit_price * li.quantity
            total_amount += tp
            line_items.append(
                QuotationLineItem(
                    rfq_line_item_id=li.rfq_line_item_id,
                    unit_price=li.unit_price,
                    quantity=li.quantity,
                    total_price=tp,
                    notes=li.notes,
                )
            )

        quotation = Quotation(
            quotation_number=generate_quotation_number(),
            rfq_id=payload.rfq_id,
            vendor_id=current_user.vendor_company_id,
            status=QuotationStatus.DRAFT,
            validity_date=payload.validity_date,
            delivery_days=payload.delivery_days,
            notes=payload.notes,
            total_amount=total_amount,
            line_items=line_items,
        )

        self.db.add(quotation)
        await self.db.commit()
        await self.db.refresh(quotation)
        return await self._get_quotation(quotation.id)

    async def update_quotation(self, quotation_id: uuid.UUID, payload: QuotationUpdate, current_user: User) -> Quotation:
        q = await self._get_quotation(quotation_id)
        if q.vendor_id != current_user.vendor_company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        if q.status != QuotationStatus.DRAFT:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only DRAFT quotations can be updated.")

        if payload.validity_date is not None:
            q.validity_date = payload.validity_date
        if payload.delivery_days is not None:
            q.delivery_days = payload.delivery_days
        if payload.notes is not None:
            q.notes = payload.notes

        await self.db.commit()
        return await self._get_quotation(quotation_id)

    async def submit_quotation(self, quotation_id: uuid.UUID, current_user: User) -> Quotation:
        q = await self._get_quotation(quotation_id)
        if q.vendor_id != current_user.vendor_company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        if q.status != QuotationStatus.DRAFT:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Quotation must be in DRAFT status to submit.")

        q.status = QuotationStatus.SUBMITTED
        q.submitted_at = datetime.now(timezone.utc)

        # Update assignment status
        assign_result = await self.db.execute(
            select(RFQVendorAssignment)
            .where(RFQVendorAssignment.rfq_id == q.rfq_id)
            .where(RFQVendorAssignment.vendor_id == q.vendor_id)
        )
        assignment = assign_result.scalar_one()
        assignment.status = AssignmentStatus.SUBMITTED

        # Notify procurement officer
        rfq_result = await self.db.execute(select(RFQ).where(RFQ.id == q.rfq_id))
        rfq = rfq_result.scalar_one()

        self.db.add(
            Notification(
                user_id=rfq.created_by,
                type=NotificationType.QUOTATION_RECEIVED,
                message=f"Quotation {q.quotation_number} submitted for RFQ '{rfq.title}'.",
                entity_type="quotation",
                entity_id=q.id,
            )
        )

        await self.db.commit()
        return await self._get_quotation(quotation_id)

    async def withdraw_quotation(self, quotation_id: uuid.UUID, current_user: User) -> Quotation:
        q = await self._get_quotation(quotation_id)
        if q.vendor_id != current_user.vendor_company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        if q.status != QuotationStatus.SUBMITTED:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only SUBMITTED quotations can be withdrawn.")

        q.status = QuotationStatus.WITHDRAWN
        await self.db.commit()
        return await self._get_quotation(quotation_id)

    async def get_quotation(self, quotation_id: uuid.UUID, current_user: User) -> Quotation:
        q = await self._get_quotation(quotation_id)
        if current_user.role == UserRole.VENDOR and q.vendor_id != current_user.vendor_company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        return q

    async def get_quotations_for_rfq(self, rfq_id: uuid.UUID) -> list[Quotation]:
        result = await self.db.execute(
            select(Quotation)
            .options(
                selectinload(Quotation.line_items),
                selectinload(Quotation.vendor)
            )
            .where(Quotation.rfq_id == rfq_id)
            .order_by(Quotation.created_at.desc())
        )
        return list(result.scalars().all())

    async def select_winner(self, quotation_id: uuid.UUID, current_user: User) -> Quotation:
        q = await self._get_quotation(quotation_id)
        
        # Validate RFQ Status
        if q.rfq.status not in (RFQStatus.SENT, RFQStatus.UNDER_REVIEW):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="RFQ must be SENT or UNDER_REVIEW to select a winner."
            )

        # Set winning quotation to SELECTED
        q.status = QuotationStatus.SELECTED
        
        # Set all other quotations for this RFQ to REJECTED
        others_result = await self.db.execute(
            select(Quotation)
            .where(Quotation.rfq_id == q.rfq_id)
            .where(Quotation.id != quotation_id)
            .where(Quotation.status == QuotationStatus.SUBMITTED)
        )
        for other_q in others_result.scalars().all():
            other_q.status = QuotationStatus.REJECTED
            
        # Set RFQ status to CLOSED
        q.rfq.status = RFQStatus.CLOSED
        q.rfq.updated_by = current_user.id
        
        # Create Notification for winning vendor
        vendor_users_result = await self.db.execute(
            select(User).where(User.vendor_company_id == q.vendor_id)
        )
        for v_user in vendor_users_result.scalars().all():
            self.db.add(
                Notification(
                    user_id=v_user.id,
                    type=NotificationType.WINNER_SELECTED,
                    message=f"Your quotation {q.quotation_number} has been selected.",
                    entity_type="quotation",
                    entity_id=q.id,
                )
            )
            
        # Create ApprovalTrigger
        trigger = ApprovalTrigger(
            rfq_id=q.rfq_id,
            quotation_id=q.id,
            vendor_id=q.vendor_id,
            amount=q.total_amount or Decimal("0.00")
        )
        self.db.add(trigger)
        
        await self.db.commit()
        return await self._get_quotation(quotation_id)

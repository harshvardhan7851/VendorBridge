"""
services/rfq_service.py
=======================
Business logic for RFQ lifecycle, line items, vendor assignments,
attachments, and the Send flow (status SENT + notifications).
"""

import uuid
import os
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.notification import Notification, NotificationType
from app.models.rfq import (
    AssignmentStatus,
    RFQ,
    RFQAttachment,
    RFQLineItem,
    RFQStatus,
    RFQVendorAssignment,
)
from app.models.user import User
from app.models.vendor import Vendor
from app.schemas.rfq import (
    AssignVendorsRequest,
    RFQCreate,
    RFQLineItemCreate,
    RFQLineItemUpdate,
    RFQUpdate,
    RFQVendorAssignmentResponse,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_rfq_number() -> str:
    """Generate a unique RFQ number: RFQ-YYYYMMDD-XXXX (4 random hex chars)."""
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:4].upper()
    return f"RFQ-{today}-{suffix}"


def _require_draft(rfq: RFQ) -> None:
    if rfq.status != RFQStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Operation not allowed — RFQ is '{rfq.status.value}', expected DRAFT.",
        )


# ===========================================================================
# RFQService
# ===========================================================================

class RFQService:
    """
    Full RFQ lifecycle:
      - CRUD on RFQs and their line items
      - Vendor assignment (with duplicate-guard)
      - File attachment storage
      - Send flow: validates, transitions status, creates Notifications
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # _get_rfq  (internal — always eager-loads sub-collections)
    # ------------------------------------------------------------------

    async def _get_rfq(self, rfq_id: uuid.UUID) -> RFQ:
        """Fetch RFQ with all sub-collections eagerly loaded. Raises 404 if missing."""
        result = await self.db.execute(
            select(RFQ)
            .options(
                selectinload(RFQ.line_items),
                selectinload(RFQ.vendor_assignments),
                selectinload(RFQ.attachments),
            )
            .where(RFQ.id == rfq_id)
        )
        rfq = result.scalar_one_or_none()
        if not rfq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RFQ '{rfq_id}' not found.",
            )
        return rfq

    # ------------------------------------------------------------------
    # create_rfq
    # ------------------------------------------------------------------

    async def create_rfq(
        self,
        payload: RFQCreate,
        created_by_id: uuid.UUID,
    ) -> RFQ:
        rfq = RFQ(
            rfq_number=_generate_rfq_number(),
            title=payload.title,
            description=payload.description,
            deadline=payload.deadline,
            status=RFQStatus.DRAFT,
            created_by=created_by_id,
            updated_by=created_by_id,
        )
        self.db.add(rfq)
        await self.db.commit()
        await self.db.refresh(rfq)
        return await self._get_rfq(rfq.id)

    # ------------------------------------------------------------------
    # list_rfqs  (role-aware)
    # ------------------------------------------------------------------

    async def list_rfqs(
        self,
        current_user: User,
        search: str | None = None,
        status_filter: RFQStatus | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[RFQ], int]:
        """
        Role visibility:
          - PROCUREMENT_OFFICER : own RFQs (created_by == user.id)
          - MANAGER / ADMIN     : all RFQs
          - VENDOR              : only RFQs where they have an assignment
        """
        from app.models.user import UserRole

        query = select(RFQ)

        if current_user.role == UserRole.PROCUREMENT_OFFICER:
            query = query.where(RFQ.created_by == current_user.id)
        elif current_user.role == UserRole.VENDOR:
            if current_user.vendor_company_id is None:
                return [], 0
            # sub-select rfq_ids where this vendor is assigned
            assigned_rfq_ids = select(RFQVendorAssignment.rfq_id).where(
                RFQVendorAssignment.vendor_id == current_user.vendor_company_id
            )
            query = query.where(RFQ.id.in_(assigned_rfq_ids))
        # MANAGER / ADMIN → no additional filter

        if search:
            term = f"%{search.lower()}%"
            query = query.where(
                or_(
                    func.lower(RFQ.title).like(term),
                    func.lower(RFQ.rfq_number).like(term),
                )
            )

        if status_filter:
            query = query.where(RFQ.status == status_filter)

        # Count
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        # Paginate — newest first
        offset = (page - 1) * size
        result = await self.db.execute(
            query.order_by(RFQ.created_at.desc()).offset(offset).limit(size)
        )
        rfqs = list(result.scalars().all())
        return rfqs, total

    # ------------------------------------------------------------------
    # get_rfq (public — detail with all sub-collections)
    # ------------------------------------------------------------------

    async def get_rfq(self, rfq_id: uuid.UUID, current_user: User) -> RFQ:
        from app.models.user import UserRole

        rfq = await self._get_rfq(rfq_id)

        # Vendor can only see RFQs they are assigned to
        if current_user.role == UserRole.VENDOR:
            vendor_ids = {va.vendor_id for va in rfq.vendor_assignments}
            if current_user.vendor_company_id not in vendor_ids:
                raise HTTPException(status_code=403, detail="Access denied.")

        return rfq

    # ------------------------------------------------------------------
    # update_rfq (DRAFT only)
    # ------------------------------------------------------------------

    async def update_rfq(
        self,
        rfq_id: uuid.UUID,
        payload: RFQUpdate,
        updated_by_id: uuid.UUID,
    ) -> RFQ:
        rfq = await self._get_rfq(rfq_id)
        _require_draft(rfq)

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(rfq, field, value)
        rfq.updated_by = updated_by_id

        await self.db.commit()
        return await self._get_rfq(rfq_id)

    # ------------------------------------------------------------------
    # close_rfq
    # ------------------------------------------------------------------

    async def close_rfq(self, rfq_id: uuid.UUID, updated_by_id: uuid.UUID) -> RFQ:
        rfq = await self._get_rfq(rfq_id)

        if rfq.status in (RFQStatus.CANCELLED, RFQStatus.CLOSED):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"RFQ is already '{rfq.status.value}'.",
            )

        rfq.status = RFQStatus.CLOSED
        rfq.updated_by = updated_by_id
        await self.db.commit()
        return await self._get_rfq(rfq_id)

    # ------------------------------------------------------------------
    # Line Items
    # ------------------------------------------------------------------

    async def add_line_item(
        self,
        rfq_id: uuid.UUID,
        payload: RFQLineItemCreate,
        updated_by_id: uuid.UUID,
    ) -> RFQLineItem:
        rfq = await self._get_rfq(rfq_id)
        _require_draft(rfq)

        item = RFQLineItem(
            rfq_id=rfq_id,
            product_name=payload.product_name,
            description=payload.description,
            quantity=payload.quantity,
            unit=payload.unit,
            updated_by=updated_by_id,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def list_line_items(self, rfq_id: uuid.UUID) -> list[RFQLineItem]:
        # Ensure RFQ exists first
        await self._get_rfq(rfq_id)
        result = await self.db.execute(
            select(RFQLineItem)
            .where(RFQLineItem.rfq_id == rfq_id)
            .order_by(RFQLineItem.created_at)
        )
        return list(result.scalars().all())

    async def _get_line_item(self, item_id: uuid.UUID) -> RFQLineItem:
        result = await self.db.execute(
            select(RFQLineItem).where(RFQLineItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Line item '{item_id}' not found.",
            )
        return item

    async def update_line_item(
        self,
        item_id: uuid.UUID,
        payload: RFQLineItemUpdate,
        updated_by_id: uuid.UUID,
    ) -> RFQLineItem:
        item = await self._get_line_item(item_id)
        rfq = await self._get_rfq(item.rfq_id)
        _require_draft(rfq)

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        item.updated_by = updated_by_id

        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete_line_item(self, item_id: uuid.UUID) -> None:
        item = await self._get_line_item(item_id)
        rfq = await self._get_rfq(item.rfq_id)
        _require_draft(rfq)
        await self.db.delete(item)
        await self.db.commit()

    # ------------------------------------------------------------------
    # Vendor Assignments
    # ------------------------------------------------------------------

    async def assign_vendors(
        self,
        rfq_id: uuid.UUID,
        payload: AssignVendorsRequest,
        updated_by_id: uuid.UUID,
    ) -> list[RFQVendorAssignment]:
        rfq = await self._get_rfq(rfq_id)
        _require_draft(rfq)

        # Fetch already-assigned vendor IDs
        existing_result = await self.db.execute(
            select(RFQVendorAssignment.vendor_id).where(
                RFQVendorAssignment.rfq_id == rfq_id
            )
        )
        existing_ids: set[uuid.UUID] = {r for r in existing_result.scalars()}

        # Validate all vendor IDs exist
        new_ids = [vid for vid in payload.vendor_ids if vid not in existing_ids]
        if new_ids:
            vendor_check = await self.db.execute(
                select(Vendor.id).where(Vendor.id.in_(new_ids))
            )
            found_ids = {r for r in vendor_check.scalars()}
            missing = set(new_ids) - found_ids
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Vendor(s) not found: {', '.join(str(m) for m in missing)}",
                )

        # Create assignments for new vendors (skip duplicates silently)
        now = datetime.now(timezone.utc)
        for vendor_id in new_ids:
            self.db.add(
                RFQVendorAssignment(
                    rfq_id=rfq_id,
                    vendor_id=vendor_id,
                    status=AssignmentStatus.INVITED,
                    invited_at=now,
                )
            )

        rfq.updated_by = updated_by_id
        await self.db.commit()

        # Query assignments directly (avoids stale selectinload cache)
        result = await self.db.execute(
            select(RFQVendorAssignment)
            .where(RFQVendorAssignment.rfq_id == rfq_id)
            .order_by(RFQVendorAssignment.created_at)
        )
        return list(result.scalars().all())

    async def list_assigned_vendors(
        self, rfq_id: uuid.UUID
    ) -> list[RFQVendorAssignmentResponse]:
        """Return assignments enriched with vendor company_name."""
        await self._get_rfq(rfq_id)  # 404 guard

        result = await self.db.execute(
            select(RFQVendorAssignment, Vendor.company_name)
            .join(Vendor, RFQVendorAssignment.vendor_id == Vendor.id)
            .where(RFQVendorAssignment.rfq_id == rfq_id)
            .order_by(RFQVendorAssignment.created_at)
        )
        rows = result.all()

        assignments = []
        for assignment, company_name in rows:
            resp = RFQVendorAssignmentResponse(
                id=assignment.id,
                rfq_id=assignment.rfq_id,
                vendor_id=assignment.vendor_id,
                vendor_name=company_name,
                status=assignment.status,
                invited_at=assignment.invited_at,
                created_at=assignment.created_at,
            )
            assignments.append(resp)
        return assignments

    # ------------------------------------------------------------------
    # Attachments
    # ------------------------------------------------------------------

    async def upload_attachment(
        self,
        rfq_id: uuid.UUID,
        file: UploadFile,
        uploaded_by_id: uuid.UUID,
    ) -> RFQAttachment:
        """Save uploaded file to media/attachments/{rfq_id}/, record in DB."""
        await self._get_rfq(rfq_id)  # 404 guard

        # Build directory
        upload_dir = f"/app/media/attachments/{rfq_id}"
        os.makedirs(upload_dir, exist_ok=True)

        # Sanitise filename + avoid collisions with a uuid prefix
        safe_name = os.path.basename(file.filename or "upload")
        unique_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
        file_path = os.path.join(upload_dir, unique_name)

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        attachment = RFQAttachment(
            rfq_id=rfq_id,
            uploaded_by=uploaded_by_id,
            filename=safe_name,
            file_path=file_path,
            file_size=len(contents),
        )
        self.db.add(attachment)
        await self.db.commit()
        await self.db.refresh(attachment)
        return attachment

    async def list_attachments(self, rfq_id: uuid.UUID) -> list[RFQAttachment]:
        await self._get_rfq(rfq_id)  # 404 guard
        result = await self.db.execute(
            select(RFQAttachment)
            .where(RFQAttachment.rfq_id == rfq_id)
            .order_by(RFQAttachment.uploaded_at)
        )
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Send RFQ
    # ------------------------------------------------------------------

    async def send_rfq(
        self,
        rfq_id: uuid.UUID,
        updated_by_id: uuid.UUID,
    ) -> RFQ:
        """
        Validates prerequisites then transitions RFQ to SENT.

        Preconditions:
          - RFQ must be DRAFT
          - At least one line item must exist
          - At least one vendor must be assigned

        Side effects:
          - Sets status = SENT
          - Sets invited_at = now() on all INVITED assignments
          - Creates one Notification per assigned vendor's users (type: RFQ_INVITE)
        """
        rfq = await self._get_rfq(rfq_id)
        _require_draft(rfq)

        if not rfq.line_items:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot send RFQ with no line items. Add at least one item first.",
            )

        if not rfq.vendor_assignments:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot send RFQ with no assigned vendors. Assign at least one vendor first.",
            )

        now = datetime.now(timezone.utc)

        # Transition status
        rfq.status = RFQStatus.SENT
        rfq.updated_by = updated_by_id

        # Update invited_at for all INVITED assignments
        for assignment in rfq.vendor_assignments:
            if assignment.status == AssignmentStatus.INVITED:
                assignment.invited_at = now

        # Create Notification for each vendor's users
        vendor_ids = [va.vendor_id for va in rfq.vendor_assignments]
        if vendor_ids:
            user_result = await self.db.execute(
                select(User).where(User.vendor_company_id.in_(vendor_ids))
            )
            vendor_users: list[User] = list(user_result.scalars().all())

            for user in vendor_users:
                self.db.add(
                    Notification(
                        user_id=user.id,
                        type=NotificationType.RFQ_INVITE,
                        message=(
                            f"You have been invited to submit a quotation for "
                            f"'{rfq.title}' ({rfq.rfq_number})."
                        ),
                        entity_type="rfq",
                        entity_id=rfq.id,
                    )
                )

        await self.db.commit()
        return await self._get_rfq(rfq_id)

"""
services/po_service.py
======================
Purchase Order logic.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.enums.module3 import POStatus, ApprovalStatus
from app.models.approval import ApprovalRequest
from app.models.purchase_order import PurchaseOrder, POLineItem
from app.models.quotation import QuotationLineItem
from app.models.user import User, UserRole
from app.models.vendor import Vendor
from app.schemas.purchase_order import POStatusUpdate
from app.services.activity_log_service import log_activity
from app.services.tax_service import calculate_taxes
from app.utils.reference_generator import generate_po_number
from app.services.pdf_service import generate_po_pdf
from app.services.email_service import send_po_email

class POService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_po(self, approval_id: uuid.UUID, created_by_user_id: uuid.UUID) -> PurchaseOrder:
        # Get approval request
        approval_query = await self.db.execute(select(ApprovalRequest).where(ApprovalRequest.id == approval_id))
        approval = approval_query.scalar_one_or_none()
        if not approval:
            raise HTTPException(status_code=404, detail="Approval request not found.")
        
        if approval.status != ApprovalStatus.APPROVED:
            raise HTTPException(status_code=400, detail="Approval request is not APPROVED.")
            
        # Check if PO already exists
        existing_po = await self.db.execute(select(PurchaseOrder).where(PurchaseOrder.approval_request_id == approval_id))
        if existing_po.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="A Purchase Order already exists for this approval request.")
            
        # Copy line items
        ql_query = await self.db.execute(select(QuotationLineItem).where(QuotationLineItem.quotation_id == approval.quotation_id))
        quotation_lines = ql_query.scalars().all()
        
        subtotal = sum((line.total_price for line in quotation_lines), Decimal("0.00"))
        taxes = calculate_taxes(subtotal)
        
        po = PurchaseOrder(
            po_number=generate_po_number(),
            approval_request_id=approval_id,
            vendor_id=approval.vendor_id,
            rfq_id=approval.rfq_id,
            quotation_id=approval.quotation_id,
            created_by=created_by_user_id,
            subtotal=subtotal,
            cgst=taxes["cgst"],
            sgst=taxes["sgst"],
            igst=taxes["igst"],
            grand_total=taxes["grand_total"],
            status=POStatus.DRAFT,
            issued_date=None
        )
        self.db.add(po)
        await self.db.flush()
        
        for ql in quotation_lines:
            po_line = POLineItem(
                purchase_order_id=po.id,
                product_name=ql.rfq_line_item.product_name if hasattr(ql, "rfq_line_item") else "Item",
                description=ql.rfq_line_item.description if hasattr(ql, "rfq_line_item") else "",
                quantity=ql.quantity,
                unit_price=ql.unit_price,
                total_price=ql.total_price
            )
            self.db.add(po_line)
            
        await log_activity(
            self.db,
            user_id=created_by_user_id,
            action="PO_GENERATED",
            entity_type="purchase_order",
            entity_id=po.id,
            new_values={"po_number": po.po_number, "grand_total": str(taxes["grand_total"])}
        )
        
        await self.db.commit()
        await self.db.refresh(po, ["line_items"])
        return po

    async def _get_po_or_404(self, po_id: uuid.UUID) -> PurchaseOrder:
        query = select(PurchaseOrder).options(selectinload(PurchaseOrder.line_items)).where(PurchaseOrder.id == po_id)
        result = await self.db.execute(query)
        po = result.scalar_one_or_none()
        if not po:
            raise HTTPException(status_code=404, detail="Purchase Order not found.")
        return po

    async def update_po_status(self, po_id: uuid.UUID, new_status: str, user_id: uuid.UUID) -> PurchaseOrder:
        po = await self._get_po_or_404(po_id)
        old_status = po.status
        po.status = new_status
        if new_status == POStatus.ISSUED and not po.issued_date:
            po.issued_date = datetime.now(timezone.utc).date()
            
        await log_activity(self.db, user_id, "PO_STATUS_UPDATED", "purchase_order", po.id, {"status": old_status}, {"status": new_status})
        await self.db.commit()
        await self.db.refresh(po, ["line_items"])
        return po

    async def generate_po_pdf_and_attach(self, po_id: uuid.UUID) -> str:
        po = await self._get_po_or_404(po_id)
        vendor = (await self.db.execute(select(Vendor).where(Vendor.id == po.vendor_id))).scalar_one()
        pdf_path = generate_po_pdf(po, po.line_items, vendor)
        return pdf_path

    async def send_po_email_service(self, po_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        po = await self._get_po_or_404(po_id)
        vendor = (await self.db.execute(select(Vendor).where(Vendor.id == po.vendor_id))).scalar_one()
        pdf_path = generate_po_pdf(po, po.line_items, vendor)
        
        await send_po_email(vendor.email, vendor.company_name, po.po_number, pdf_path)
        
        await log_activity(self.db, user_id, "PO_EMAIL_SENT", "purchase_order", po.id)
        await self.db.commit()
        return {"message": f"PO emailed to {vendor.email}"}

    async def list_pos(self, user: User, status_filter: str | None, vendor_id: uuid.UUID | None, page: int = 1, size: int = 20) -> tuple[list[PurchaseOrder], int]:
        query = select(PurchaseOrder)
        
        if user.role == UserRole.VENDOR:
            query = query.where(PurchaseOrder.vendor_id == user.vendor_company_id)
        elif vendor_id:
            query = query.where(PurchaseOrder.vendor_id == vendor_id)
            
        if status_filter:
            query = query.where(PurchaseOrder.status == status_filter)
            
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()
        
        offset = (page - 1) * size
        query = query.order_by(PurchaseOrder.created_at.desc()).offset(offset).limit(size).options(selectinload(PurchaseOrder.line_items))
        
        pos = list((await self.db.execute(query)).scalars().all())
        return pos, total

    async def get_po_detail(self, po_id: uuid.UUID, user: User) -> PurchaseOrder:
        po = await self._get_po_or_404(po_id)
        if user.role == UserRole.VENDOR and po.vendor_id != user.vendor_company_id:
            raise HTTPException(status_code=403, detail="Access denied.")
        return po

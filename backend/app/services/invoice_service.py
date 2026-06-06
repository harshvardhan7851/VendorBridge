"""
services/invoice_service.py
===========================
Invoice logic.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.enums.module3 import InvoiceStatus, POStatus
from app.models.purchase_order import PurchaseOrder, POLineItem
from app.models.invoice import Invoice, InvoiceLineItem
from app.models.user import User, UserRole
from app.models.vendor import Vendor
from app.services.activity_log_service import log_activity
from app.utils.reference_generator import generate_invoice_internal_reference
from app.services.pdf_service import generate_invoice_pdf
from app.services.email_service import send_invoice_email

class InvoiceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_invoice(self, po_id: uuid.UUID, created_by_user_id: uuid.UUID) -> Invoice:
        po_query = await self.db.execute(select(PurchaseOrder).options(selectinload(PurchaseOrder.line_items)).where(PurchaseOrder.id == po_id))
        po = po_query.scalar_one_or_none()
        if not po:
            raise HTTPException(status_code=404, detail="Purchase Order not found.")
            
        if po.status not in (POStatus.ISSUED, POStatus.ACCEPTED):
            raise HTTPException(status_code=400, detail="PO must be ISSUED or ACCEPTED to generate an invoice.")
            
        existing_invoice = await self.db.execute(select(Invoice).where(Invoice.purchase_order_id == po_id, Invoice.status != InvoiceStatus.DRAFT)) # Let's just say one invoice per PO for simplicity.
        if existing_invoice.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="An invoice already exists for this PO.")
            
        tax_amount = po.cgst + po.sgst + po.igst
            
        invoice = Invoice(
            invoice_number=generate_invoice_internal_reference(),
            purchase_order_id=po.id,
            vendor_id=po.vendor_id,
            invoice_date=datetime.now(timezone.utc).date(),
            subtotal=po.subtotal,
            tax_amount=tax_amount,
            grand_total=po.grand_total,
            status=InvoiceStatus.DRAFT,
            pdf_url=None,
            email_sent=False
        )
        self.db.add(invoice)
        await self.db.flush()
        
        for pl in po.line_items:
            inv_line = InvoiceLineItem(
                invoice_id=invoice.id,
                description=pl.product_name,
                quantity=pl.quantity,
                unit_price=pl.unit_price,
                total_price=pl.total_price
            )
            self.db.add(inv_line)
            
        await log_activity(
            self.db,
            user_id=created_by_user_id,
            action="INVOICE_GENERATED",
            entity_type="invoice",
            entity_id=invoice.id,
            new_values={"invoice_number": invoice.invoice_number, "grand_total": str(invoice.grand_total)}
        )
        
        await self.db.commit()
        await self.db.refresh(invoice, ["line_items"])
        return invoice

    async def _get_invoice_or_404(self, invoice_id: uuid.UUID) -> Invoice:
        query = select(Invoice).options(selectinload(Invoice.line_items)).where(Invoice.id == invoice_id)
        result = await self.db.execute(query)
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found.")
        return invoice

    async def update_invoice_status(self, invoice_id: uuid.UUID, new_status: str, user_id: uuid.UUID) -> Invoice:
        invoice = await self._get_invoice_or_404(invoice_id)
        old_status = invoice.status
        invoice.status = new_status
        await log_activity(self.db, user_id, "INVOICE_STATUS_UPDATED", "invoice", invoice.id, {"status": old_status}, {"status": new_status})
        await self.db.commit()
        await self.db.refresh(invoice, ["line_items"])
        return invoice

    async def generate_invoice_pdf_and_attach(self, invoice_id: uuid.UUID) -> str:
        invoice = await self._get_invoice_or_404(invoice_id)
        vendor = (await self.db.execute(select(Vendor).where(Vendor.id == invoice.vendor_id))).scalar_one()
        po = (await self.db.execute(select(PurchaseOrder).where(PurchaseOrder.id == invoice.purchase_order_id))).scalar_one()
        
        pdf_path = generate_invoice_pdf(invoice, invoice.line_items, vendor, po)
        invoice.pdf_url = pdf_path
        await self.db.commit()
        return pdf_path

    async def send_invoice_email_service(self, invoice_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        invoice = await self._get_invoice_or_404(invoice_id)
        vendor = (await self.db.execute(select(Vendor).where(Vendor.id == invoice.vendor_id))).scalar_one()
        
        if not invoice.pdf_url:
            po = (await self.db.execute(select(PurchaseOrder).where(PurchaseOrder.id == invoice.purchase_order_id))).scalar_one()
            invoice.pdf_url = generate_invoice_pdf(invoice, invoice.line_items, vendor, po)
            
        await send_invoice_email(vendor.email, vendor.company_name, invoice.invoice_number, invoice.pdf_url)
        invoice.email_sent = True
        
        await log_activity(self.db, user_id, "INVOICE_EMAIL_SENT", "invoice", invoice.id)
        await self.db.commit()
        return {"message": f"Invoice emailed to {vendor.email}"}

    async def list_invoices(self, user: User, status_filter: str | None, vendor_id: uuid.UUID | None, page: int = 1, size: int = 20) -> tuple[list[Invoice], int]:
        query = select(Invoice)
        
        if user.role == UserRole.VENDOR:
            query = query.where(Invoice.vendor_id == user.vendor_company_id)
        elif vendor_id:
            query = query.where(Invoice.vendor_id == vendor_id)
            
        if status_filter:
            query = query.where(Invoice.status == status_filter)
            
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()
        
        offset = (page - 1) * size
        query = query.order_by(Invoice.created_at.desc()).offset(offset).limit(size).options(selectinload(Invoice.line_items))
        
        invoices = list((await self.db.execute(query)).scalars().all())
        return invoices, total

    async def get_invoice_detail(self, invoice_id: uuid.UUID, user: User) -> Invoice:
        invoice = await self._get_invoice_or_404(invoice_id)
        if user.role == UserRole.VENDOR and invoice.vendor_id != user.vendor_company_id:
            raise HTTPException(status_code=403, detail="Access denied.")
        return invoice

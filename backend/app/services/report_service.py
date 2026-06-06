"""
services/report_service.py
==========================
Reporting and Export Logic.
"""

import csv
import io
from decimal import Decimal

from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.approval import ApprovalRequest
from app.models.purchase_order import PurchaseOrder
from app.models.invoice import Invoice
from app.models.rfq import RFQ
from app.models.vendor import Vendor
from app.enums.module3 import ApprovalStatus, POStatus

class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_procurement_summary(self) -> dict:
        total_rfqs = (await self.db.execute(select(func.count(RFQ.id)))).scalar_one()
        total_pos = (await self.db.execute(select(func.count(PurchaseOrder.id)))).scalar_one()
        total_invoices = (await self.db.execute(select(func.count(Invoice.id)))).scalar_one()
        
        spend_query = select(func.sum(PurchaseOrder.grand_total)).where(PurchaseOrder.status != POStatus.CANCELLED)
        total_spend = (await self.db.execute(spend_query)).scalar_one_or_none() or Decimal("0.00")
        
        pending_approvals = (await self.db.execute(select(func.count(ApprovalRequest.id)).where(ApprovalRequest.status == ApprovalStatus.PENDING))).scalar_one()
        
        return {
            "total_rfqs": total_rfqs,
            "total_purchase_orders": total_pos,
            "total_invoices": total_invoices,
            "total_spend": total_spend,
            "pending_approvals": pending_approvals
        }

    async def get_vendor_performance(self) -> list[dict]:
        # Group by vendor on POs
        query = select(
            PurchaseOrder.vendor_id,
            func.count(PurchaseOrder.id).label("approved_orders"),
            func.sum(PurchaseOrder.grand_total).label("total_spend"),
            func.avg(PurchaseOrder.grand_total).label("average_order_value")
        ).where(PurchaseOrder.status != POStatus.CANCELLED).group_by(PurchaseOrder.vendor_id)
        
        results = await self.db.execute(query)
        performance = []
        
        for row in results.all():
            vendor = (await self.db.execute(select(Vendor).where(Vendor.id == row.vendor_id))).scalar_one()
            performance.append({
                "vendor_id": vendor.id,
                "vendor_name": vendor.company_name,
                "approved_orders": row.approved_orders,
                "total_spend": row.total_spend or Decimal("0.00"),
                "average_order_value": row.average_order_value or Decimal("0.00")
            })
            
        return performance

    async def get_monthly_spend(self) -> list[dict]:
        # PostgreSQL specific date truncation
        query = select(
            func.to_char(PurchaseOrder.created_at, 'YYYY-MM').label("month"),
            func.sum(PurchaseOrder.grand_total).label("amount")
        ).where(PurchaseOrder.status != POStatus.CANCELLED).group_by("month").order_by("month")
        
        results = await self.db.execute(query)
        return [{"month": row.month, "amount": row.amount or Decimal("0.00")} for row in results.all()]

    async def export_vendors_csv(self) -> str:
        query = select(
            Vendor,
            func.count(distinct(PurchaseOrder.id)).label("total_orders"),
            func.sum(PurchaseOrder.grand_total).label("total_spend")
        ).outerjoin(PurchaseOrder, Vendor.id == PurchaseOrder.vendor_id).group_by(Vendor.id)
        
        results = await self.db.execute(query)
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["vendor_name", "email", "status", "total_orders", "total_spend"])
        
        for vendor, total_orders, total_spend in results.all():
            writer.writerow([
                vendor.company_name,
                vendor.email,
                vendor.status.value if hasattr(vendor.status, 'value') else vendor.status,
                total_orders,
                total_spend or "0.00"
            ])
            
        return output.getvalue()

    async def export_procurement_csv(self) -> str:
        query = select(PurchaseOrder, Vendor, RFQ).join(Vendor, PurchaseOrder.vendor_id == Vendor.id).join(RFQ, PurchaseOrder.rfq_id == RFQ.id)
        results = await self.db.execute(query)
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["po_number", "rfq_number", "vendor_name", "subtotal", "tax_amount", "grand_total", "status", "issued_date"])
        
        for po, vendor, rfq in results.all():
            writer.writerow([
                po.po_number,
                rfq.rfq_number,
                vendor.company_name,
                po.subtotal,
                po.cgst + po.sgst + po.igst,
                po.grand_total,
                po.status.value if hasattr(po.status, 'value') else po.status,
                po.issued_date or ""
            ])
            
        return output.getvalue()

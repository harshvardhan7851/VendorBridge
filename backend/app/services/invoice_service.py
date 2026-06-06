"""
Invoice Service — stub methods only.
"""
from sqlalchemy.ext.asyncio import AsyncSession


class InvoiceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_invoices(self, filters=None):
        # TODO: Filter by vendor, PO, status, date range
        raise NotImplementedError

    async def create_invoice(self, data: dict, vendor_id: str):
        # TODO: Validate PO exists, check amount doesn't exceed PO total
        raise NotImplementedError

    async def get_invoice(self, invoice_id: str):
        raise NotImplementedError

    async def approve_invoice(self, invoice_id: str, approver_id: str):
        # TODO: Set status="approved", initiate payment notification
        raise NotImplementedError

    async def reject_invoice(self, invoice_id: str, reason: str, approver_id: str):
        # TODO: Set status="rejected", notify vendor with reason
        raise NotImplementedError

    async def record_payment(self, invoice_id: str, amount: float, payment_date: str):
        # TODO: Update amount_paid, update status to "paid" or "partially_paid"
        raise NotImplementedError

"""
Quotation Service — stub methods only.
"""
from sqlalchemy.ext.asyncio import AsyncSession


class QuotationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_quotations(self, rfq_id=None, vendor_id=None, status=None):
        # TODO: Query quotations with optional filters
        raise NotImplementedError

    async def create_quotation(self, data: dict, vendor_id: str):
        # TODO: Validate RFQ is published and deadline not passed
        raise NotImplementedError

    async def get_quotation(self, quotation_id: str):
        # TODO: Return with line items eager-loaded
        raise NotImplementedError

    async def update_quotation(self, quotation_id: str, data: dict):
        # TODO: Only allow updates in "draft" status
        raise NotImplementedError

    async def award_quotation(self, quotation_id: str, awarded_by: str):
        # TODO: Mark quotation "awarded", auto-create PurchaseOrder skeleton
        raise NotImplementedError

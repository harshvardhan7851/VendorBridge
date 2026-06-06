"""
RFQ Service
===========
Business logic for RFQ management.
All methods are stubs with TODO comments only.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class RFQService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_rfqs(self, filters=None, page=1, size=20):
        # TODO: Paginated query with filters (status, category, date range)
        raise NotImplementedError

    async def create_rfq(self, rfq_data: dict, created_by: str):
        # TODO: Auto-generate rfq_number (e.g., RFQ-2024-001), insert RFQ + line items
        raise NotImplementedError

    async def get_rfq(self, rfq_id: str):
        # TODO: Eager-load line_items, return full RFQResponse
        raise NotImplementedError

    async def update_rfq(self, rfq_id: str, update_data: dict):
        # TODO: Only allow updates in "draft" status
        raise NotImplementedError

    async def cancel_rfq(self, rfq_id: str):
        # TODO: Set status="cancelled", notify assigned vendors
        raise NotImplementedError

    async def publish_rfq(self, rfq_id: str, vendor_ids: list):
        # TODO: Set status="published", send invitation emails to vendors
        raise NotImplementedError

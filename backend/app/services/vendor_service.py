"""
Vendor Service
==============
Business logic for vendor management.
All methods are stubs with TODO comments only.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class VendorService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_vendors(self, status=None, category=None, page=1, size=20):
        # TODO: Query vendors with optional filters, return paginated result
        raise NotImplementedError

    async def create_vendor(self, vendor_data: dict):
        # TODO: Validate uniqueness, create Vendor record, notify admin
        raise NotImplementedError

    async def get_vendor(self, vendor_id: str):
        # TODO: Fetch by ID, raise 404 if not found
        raise NotImplementedError

    async def update_vendor(self, vendor_id: str, update_data: dict):
        # TODO: Apply partial update, return VendorResponse
        raise NotImplementedError

    async def deactivate_vendor(self, vendor_id: str):
        # TODO: Soft-delete (is_active=False)
        raise NotImplementedError

    async def approve_vendor(self, vendor_id: str, approver_id: str):
        # TODO: Set status="approved", send approval email, create Notification
        raise NotImplementedError

    async def reject_vendor(self, vendor_id: str, reason: str, approver_id: str):
        # TODO: Set status="rejected", send rejection email with reason
        raise NotImplementedError

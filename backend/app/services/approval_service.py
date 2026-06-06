"""
Approval Service — stub methods only.
"""
from sqlalchemy.ext.asyncio import AsyncSession


class ApprovalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_approvals(self, approver_id=None, status=None):
        # TODO: Return approvals filtered by approver and status
        raise NotImplementedError

    async def get_approval(self, approval_id: str):
        # TODO: Fetch approval with linked entity details
        raise NotImplementedError

    async def approve(self, approval_id: str, approver_id: str, comments: str = ""):
        # TODO: Set status="approved", trigger downstream workflow, create Notification
        raise NotImplementedError

    async def reject(self, approval_id: str, approver_id: str, comments: str):
        # TODO: Set status="rejected", notify requester
        raise NotImplementedError

    async def create_approval_request(self, data: dict, requester_id: str):
        # TODO: Create ApprovalRequest record, assign to manager/admin, send notification
        raise NotImplementedError

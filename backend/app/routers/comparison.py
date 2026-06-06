"""
routers/comparison.py
=====================
Comparison Engine API endpoints under /api/v1/comparison.
"""

import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user, require_roles
from app.models.user import User, UserRole
from app.services.comparison_service import ComparisonService

router = APIRouter()

def _ok(data=None, message: str = "") -> dict:
    return {"success": True, "data": data, "message": message}

@router.get("/rfq/{rfq_id}", summary="Get RFQ Comparison (Officer/Manager)")
async def get_rfq_comparison(
    rfq_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER, UserRole.MANAGER)),
) -> dict:
    svc = ComparisonService(db)
    comparison_data = await svc.get_rfq_comparison(rfq_id)
    return _ok(data=comparison_data)

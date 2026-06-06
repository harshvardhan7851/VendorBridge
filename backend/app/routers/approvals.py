"""
routers/approvals.py
"""
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.pagination import PagedResponse
from app.schemas.approval import ApprovalCreate, ApprovalDecisionRequest, ApprovalResponse
from app.services.approval_service import ApprovalService

router = APIRouter()

def _ok(data=None, message=""):
    return {"success": True, "data": data, "message": message}

@router.post("/", response_model=dict)
async def create_approval(
    payload: ApprovalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER))
):
    service = ApprovalService(db)
    approval = await service.create_approval_request(payload, current_user.id)
    return _ok(ApprovalResponse.model_validate(approval).model_dump(), "Approval created")

@router.get("/", response_model=dict)
async def list_approvals(
    status: str = Query(None),
    date: str = Query(None),
    min_amount: float = Query(None),
    max_amount: float = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER, UserRole.MANAGER))
):
    service = ApprovalService(db)
    approvals, total = await service.list_approvals(current_user, status, date, min_amount, max_amount, page, page_size)
    data = [ApprovalResponse.model_validate(a).model_dump() for a in approvals]
    return _ok(PagedResponse(items=data, total=total, page=page, size=page_size).model_dump())

@router.get("/{id}", response_model=dict)
async def get_approval(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER, UserRole.MANAGER))
):
    service = ApprovalService(db)
    approval = await service.get_approval_detail(id)
    return _ok(ApprovalResponse.model_validate(approval).model_dump())

@router.post("/{id}/approve", response_model=dict)
async def approve_request(
    id: uuid.UUID,
    payload: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.MANAGER))
):
    service = ApprovalService(db)
    approval = await service.approve_request(id, current_user.id, payload)
    return _ok(ApprovalResponse.model_validate(approval).model_dump(), "Approved")

@router.post("/{id}/reject", response_model=dict)
async def reject_request(
    id: uuid.UUID,
    payload: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.MANAGER))
):
    service = ApprovalService(db)
    approval = await service.reject_request(id, current_user.id, payload)
    return _ok(ApprovalResponse.model_validate(approval).model_dump(), "Rejected")

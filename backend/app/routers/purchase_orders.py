"""
routers/purchase_orders.py
"""
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.pagination import PagedResponse
from app.schemas.purchase_order import POResponse, POStatusUpdate
from app.services.po_service import POService

router = APIRouter()

def _ok(data=None, message=""):
    return {"success": True, "data": data, "message": message}

@router.post("/generate/{approval_id}", response_model=dict)
async def generate_po(
    approval_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER))
):
    service = POService(db)
    po = await service.generate_po(approval_id, current_user.id)
    return _ok(POResponse.model_validate(po).model_dump(), "PO generated")

@router.get("/", response_model=dict)
async def list_pos(
    status: str = Query(None),
    vendor_id: uuid.UUID = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER, UserRole.MANAGER, UserRole.VENDOR))
):
    service = POService(db)
    pos, total = await service.list_pos(current_user, status, vendor_id, page, page_size)
    data = [POResponse.model_validate(p).model_dump() for p in pos]
    return _ok(PagedResponse(items=data, total=total, page=page, size=page_size).model_dump())

@router.get("/{id}", response_model=dict)
async def get_po(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER, UserRole.MANAGER, UserRole.VENDOR))
):
    service = POService(db)
    po = await service.get_po_detail(id, current_user)
    return _ok(POResponse.model_validate(po).model_dump())

@router.patch("/{id}/status", response_model=dict)
async def update_po_status(
    id: uuid.UUID,
    payload: POStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER))
):
    service = POService(db)
    po = await service.update_po_status(id, payload.status.value, current_user.id)
    return _ok(POResponse.model_validate(po).model_dump(), "Status updated")

@router.get("/{id}/pdf", response_model=dict)
async def get_po_pdf(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER, UserRole.MANAGER, UserRole.VENDOR))
):
    service = POService(db)
    pdf_path = await service.generate_po_pdf_and_attach(id)
    return _ok({"pdf_url": pdf_path})

@router.post("/{id}/send-email", response_model=dict)
async def send_po_email(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER))
):
    service = POService(db)
    result = await service.send_po_email_service(id, current_user.id)
    return _ok(result, "Email sent")

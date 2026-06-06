"""
routers/invoices.py
"""
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.pagination import PagedResponse
from app.schemas.invoice import InvoiceResponse, InvoiceStatusUpdate
from app.services.invoice_service import InvoiceService

router = APIRouter()

def _ok(data=None, message=""):
    return {"success": True, "data": data, "message": message}

@router.post("/generate/{po_id}", response_model=dict)
async def generate_invoice(
    po_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER))
):
    service = InvoiceService(db)
    invoice = await service.generate_invoice(po_id, current_user.id)
    return _ok(InvoiceResponse.model_validate(invoice).model_dump(), "Invoice generated")

@router.get("/", response_model=dict)
async def list_invoices(
    status: str = Query(None),
    vendor_id: uuid.UUID = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER, UserRole.MANAGER, UserRole.VENDOR))
):
    service = InvoiceService(db)
    invoices, total = await service.list_invoices(current_user, status, vendor_id, page, page_size)
    data = [InvoiceResponse.model_validate(i).model_dump() for i in invoices]
    return _ok(PagedResponse(items=data, total=total, page=page, size=page_size).model_dump())

@router.get("/{id}", response_model=dict)
async def get_invoice(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER, UserRole.MANAGER, UserRole.VENDOR))
):
    service = InvoiceService(db)
    invoice = await service.get_invoice_detail(id, current_user)
    return _ok(InvoiceResponse.model_validate(invoice).model_dump())

@router.patch("/{id}/status", response_model=dict)
async def update_invoice_status(
    id: uuid.UUID,
    payload: InvoiceStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER))
):
    service = InvoiceService(db)
    invoice = await service.update_invoice_status(id, payload.status.value, current_user.id)
    return _ok(InvoiceResponse.model_validate(invoice).model_dump(), "Status updated")

@router.get("/{id}/pdf", response_model=dict)
async def get_invoice_pdf(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER, UserRole.MANAGER, UserRole.VENDOR))
):
    service = InvoiceService(db)
    pdf_path = await service.generate_invoice_pdf_and_attach(id)
    return _ok({"pdf_url": pdf_path})

@router.post("/{id}/send-email", response_model=dict)
async def send_invoice_email(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER))
):
    service = InvoiceService(db)
    result = await service.send_invoice_email_service(id, current_user.id)
    return _ok(result, "Email sent")

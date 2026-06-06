"""
routers/quotations.py
=====================
Quotation API endpoints under /api/v1/quotations.
"""

import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.quotation import QuotationCreate, QuotationUpdate, QuotationDetail
from app.services.quotation_service import QuotationService

router = APIRouter()

def _ok(data=None, message: str = "") -> dict:
    return {"success": True, "data": data, "message": message}

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create Quotation Draft (Vendor)")
async def create_quotation(
    payload: QuotationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.VENDOR)),
) -> dict:
    svc = QuotationService(db)
    q = await svc.create_quotation(payload, current_user)
    return _ok(
        data=QuotationDetail.model_validate(q).model_dump(mode="json"),
        message="Quotation draft created."
    )

@router.put("/{quotation_id}", summary="Update Quotation Draft (Vendor)")
async def update_quotation(
    quotation_id: uuid.UUID,
    payload: QuotationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.VENDOR)),
) -> dict:
    svc = QuotationService(db)
    q = await svc.update_quotation(quotation_id, payload, current_user)
    return _ok(
        data=QuotationDetail.model_validate(q).model_dump(mode="json"),
        message="Quotation updated."
    )

@router.post("/{quotation_id}/submit", summary="Submit Quotation (Vendor)")
async def submit_quotation(
    quotation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.VENDOR)),
) -> dict:
    svc = QuotationService(db)
    q = await svc.submit_quotation(quotation_id, current_user)
    return _ok(
        data=QuotationDetail.model_validate(q).model_dump(mode="json"),
        message="Quotation submitted."
    )

@router.post("/{quotation_id}/withdraw", summary="Withdraw Quotation (Vendor)")
async def withdraw_quotation(
    quotation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.VENDOR)),
) -> dict:
    svc = QuotationService(db)
    q = await svc.withdraw_quotation(quotation_id, current_user)
    return _ok(
        data=QuotationDetail.model_validate(q).model_dump(mode="json"),
        message="Quotation withdrawn."
    )

@router.get("/rfq/{rfq_id}", summary="Get all Quotations for an RFQ (Officer/Manager)")
async def get_rfq_quotations(
    rfq_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER, UserRole.MANAGER)),
) -> dict:
    svc = QuotationService(db)
    quotations = await svc.get_quotations_for_rfq(rfq_id)
    data = [QuotationDetail.model_validate(q).model_dump(mode="json") for q in quotations]
    return _ok(data=data)

@router.get("/{quotation_id}", summary="Get Quotation Detail")
async def get_quotation(
    quotation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    svc = QuotationService(db)
    q = await svc.get_quotation(quotation_id, current_user)
    return _ok(data=QuotationDetail.model_validate(q).model_dump(mode="json"))

@router.post("/{quotation_id}/select-winner", summary="Select Quotation as Winner (Officer)")
async def select_winner(
    quotation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER)),
) -> dict:
    svc = QuotationService(db)
    q = await svc.select_winner(quotation_id, current_user)
    return _ok(
        data=QuotationDetail.model_validate(q).model_dump(mode="json"),
        message="Winner selected."
    )

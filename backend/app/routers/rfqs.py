"""
routers/rfqs.py
===============
RFQ API endpoints under /api/v1/rfqs.

RFQ CRUD:
  POST   /                          Create RFQ (Officer)
  GET    /                          List RFQs (role-filtered, paginated)
  GET    /{rfq_id}                  Detail with line_items, vendors, attachments
  PUT    /{rfq_id}                  Update (Officer, DRAFT only)
  PATCH  /{rfq_id}/close            Close (Officer or Manager)

Line Items:
  POST   /{rfq_id}/line-items       Add item (Officer, DRAFT only)
  GET    /{rfq_id}/line-items       List items
  PUT    /line-items/{item_id}      Update item
  DELETE /line-items/{item_id}      Delete item

Vendor Assignment:
  POST   /{rfq_id}/assign-vendors   Assign vendors (Officer)
  GET    /{rfq_id}/assigned-vendors List assignments with status + vendor name

Attachments:
  POST   /{rfq_id}/attachments      Multipart file upload (Officer)
  GET    /{rfq_id}/attachments      List attachments

Send:
  POST   /{rfq_id}/send             Validate & send (Officer)
"""

import uuid

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user, require_roles
from app.models.rfq import RFQStatus
from app.models.user import User, UserRole
from app.schemas.pagination import PagedResponse
from app.schemas.rfq import (
    AssignVendorsRequest,
    RFQAttachmentResponse,
    RFQCreate,
    RFQDetail,
    RFQLineItemCreate,
    RFQLineItemResponse,
    RFQLineItemUpdate,
    RFQListItem,
    RFQUpdate,
    RFQVendorAssignmentResponse,
)
from app.services.rfq_service import RFQService

router = APIRouter()


def _ok(data=None, message: str = "") -> dict:
    return {"success": True, "data": data, "message": message}


# ===========================================================================
# RFQ CRUD
# ===========================================================================

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create RFQ (Procurement Officer only)",
)
async def create_rfq(
    payload: RFQCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.PROCUREMENT_OFFICER)
    ),
) -> dict:
    svc = RFQService(db)
    rfq = await svc.create_rfq(payload, created_by_id=current_user.id)
    return _ok(
        data=RFQDetail.model_validate(rfq).model_dump(mode="json"),
        message=f"RFQ '{rfq.rfq_number}' created successfully.",
    )


@router.get(
    "/",
    summary="List RFQs (role-filtered, paginated)",
)
async def list_rfqs(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, description="Search title or rfq_number"),
    rfq_status: RFQStatus | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    svc = RFQService(db)
    rfqs, total = await svc.list_rfqs(
        current_user=current_user,
        search=search,
        status_filter=rfq_status,
        page=page,
        size=size,
    )
    items = [RFQListItem.model_validate(r).model_dump(mode="json") for r in rfqs]
    paged = PagedResponse.build(items=items, total=total, page=page, size=size)
    return _ok(data=paged.model_dump())


@router.get(
    "/{rfq_id}",
    summary="Get RFQ detail (with line items, vendors, attachments)",
)
async def get_rfq(
    rfq_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    svc = RFQService(db)
    rfq = await svc.get_rfq(rfq_id, current_user=current_user)

    # Enrich vendor_assignments with company names
    assigned_vendors = await svc.list_assigned_vendors(rfq_id)

    detail = RFQDetail(
        id=rfq.id,
        rfq_number=rfq.rfq_number,
        title=rfq.title,
        description=rfq.description,
        status=rfq.status,
        deadline=rfq.deadline,
        created_by=rfq.created_by,
        created_at=rfq.created_at,
        updated_at=rfq.updated_at,
        line_items=[RFQLineItemResponse.model_validate(li) for li in rfq.line_items],
        assigned_vendors=assigned_vendors,
        attachments=[RFQAttachmentResponse.model_validate(a) for a in rfq.attachments],
    )
    return _ok(data=detail.model_dump(mode="json"))


@router.put(
    "/{rfq_id}",
    summary="Update RFQ (Officer only, DRAFT status required)",
)
async def update_rfq(
    rfq_id: uuid.UUID,
    payload: RFQUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.PROCUREMENT_OFFICER)
    ),
) -> dict:
    svc = RFQService(db)
    rfq = await svc.update_rfq(rfq_id, payload, updated_by_id=current_user.id)
    return _ok(
        data=RFQDetail.model_validate(rfq).model_dump(mode="json"),
        message="RFQ updated successfully.",
    )


@router.patch(
    "/{rfq_id}/close",
    summary="Close RFQ (Officer or Manager)",
)
async def close_rfq(
    rfq_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.PROCUREMENT_OFFICER, UserRole.MANAGER)
    ),
) -> dict:
    svc = RFQService(db)
    rfq = await svc.close_rfq(rfq_id, updated_by_id=current_user.id)
    return _ok(
        data=RFQDetail.model_validate(rfq).model_dump(mode="json"),
        message=f"RFQ '{rfq.rfq_number}' closed.",
    )


# ===========================================================================
# Line Items
# ===========================================================================

@router.post(
    "/{rfq_id}/line-items",
    status_code=status.HTTP_201_CREATED,
    summary="Add a line item to an RFQ (Officer, DRAFT only)",
)
async def add_line_item(
    rfq_id: uuid.UUID,
    payload: RFQLineItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.PROCUREMENT_OFFICER)
    ),
) -> dict:
    svc = RFQService(db)
    item = await svc.add_line_item(rfq_id, payload, updated_by_id=current_user.id)
    return _ok(
        data=RFQLineItemResponse.model_validate(item).model_dump(mode="json"),
        message="Line item added.",
    )


@router.get(
    "/{rfq_id}/line-items",
    summary="List line items for an RFQ",
)
async def list_line_items(
    rfq_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    svc = RFQService(db)
    items = await svc.list_line_items(rfq_id)
    return _ok(
        data=[RFQLineItemResponse.model_validate(i).model_dump(mode="json") for i in items]
    )


@router.put(
    "/line-items/{item_id}",
    summary="Update a line item (Officer, DRAFT only)",
)
async def update_line_item(
    item_id: uuid.UUID,
    payload: RFQLineItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.PROCUREMENT_OFFICER)
    ),
) -> dict:
    svc = RFQService(db)
    item = await svc.update_line_item(item_id, payload, updated_by_id=current_user.id)
    return _ok(
        data=RFQLineItemResponse.model_validate(item).model_dump(mode="json"),
        message="Line item updated.",
    )


@router.delete(
    "/line-items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a line item (Officer, DRAFT only)",
)
async def delete_line_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.PROCUREMENT_OFFICER)
    ),
) -> None:
    svc = RFQService(db)
    await svc.delete_line_item(item_id)


# ===========================================================================
# Vendor Assignments
# ===========================================================================

@router.post(
    "/{rfq_id}/assign-vendors",
    summary="Assign vendors to an RFQ (Officer, DRAFT only). Duplicates are skipped.",
)
async def assign_vendors(
    rfq_id: uuid.UUID,
    payload: AssignVendorsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.PROCUREMENT_OFFICER)
    ),
) -> dict:
    svc = RFQService(db)
    assignments = await svc.assign_vendors(rfq_id, payload, updated_by_id=current_user.id)
    return _ok(
        data=[
            RFQVendorAssignmentResponse.model_validate(a).model_dump(mode="json")
            for a in assignments
        ],
        message=f"{len(assignments)} vendor(s) assigned.",
    )


@router.get(
    "/{rfq_id}/assigned-vendors",
    summary="List vendors assigned to an RFQ with their assignment status",
)
async def list_assigned_vendors(
    rfq_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    svc = RFQService(db)
    assignments = await svc.list_assigned_vendors(rfq_id)
    return _ok(data=[a.model_dump(mode="json") for a in assignments])


# ===========================================================================
# Attachments
# ===========================================================================

@router.post(
    "/{rfq_id}/attachments",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file attachment to an RFQ (Officer only)",
)
async def upload_attachment(
    rfq_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.PROCUREMENT_OFFICER)
    ),
) -> dict:
    svc = RFQService(db)
    attachment = await svc.upload_attachment(rfq_id, file, uploaded_by_id=current_user.id)
    return _ok(
        data=RFQAttachmentResponse.model_validate(attachment).model_dump(mode="json"),
        message=f"File '{attachment.filename}' uploaded successfully.",
    )


@router.get(
    "/{rfq_id}/attachments",
    summary="List all attachments for an RFQ",
)
async def list_attachments(
    rfq_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    svc = RFQService(db)
    attachments = await svc.list_attachments(rfq_id)
    return _ok(
        data=[RFQAttachmentResponse.model_validate(a).model_dump(mode="json") for a in attachments]
    )


# ===========================================================================
# Send RFQ
# ===========================================================================

@router.post(
    "/{rfq_id}/send",
    summary="Send RFQ to assigned vendors (Officer only). Validates prereqs, sets status SENT, creates notifications.",
)
async def send_rfq(
    rfq_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.PROCUREMENT_OFFICER)
    ),
) -> dict:
    svc = RFQService(db)
    rfq = await svc.send_rfq(rfq_id, updated_by_id=current_user.id)
    return _ok(
        data=RFQDetail.model_validate(rfq).model_dump(mode="json"),
        message=f"RFQ '{rfq.rfq_number}' sent to {len(rfq.vendor_assignments)} vendor(s).",
    )

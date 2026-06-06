"""
routers/vendors.py
==================
Vendor management endpoints.

GET    /vendors                    Paginated list + search + filter + sort
GET    /vendors/{id}               Get vendor by ID
POST   /vendors                    Create vendor (Admin/Officer)
PUT    /vendors/{id}               Update vendor (Admin/Officer)
PATCH  /vendors/{id}/status        Update vendor status (Admin/Officer)
DELETE /vendors/{id}               Blacklist vendor (Admin only)
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.vendor import VendorStatus
from app.schemas.pagination import PagedResponse
from app.schemas.vendor import (
    VendorCreate,
    VendorFilterParams,
    VendorResponse,
    VendorStatusUpdate,
    VendorUpdate,
)
from app.services.vendor_service import VendorService

router = APIRouter()


def _ok(data=None, message: str = "") -> dict:
    return {"success": True, "data": data, "message": message}


# ---------------------------------------------------------------------------
# GET /vendors
# ---------------------------------------------------------------------------

@router.get("/", summary="List vendors (paginated, filtered, sorted)")
async def list_vendors(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, description="Search by company name"),
    status: VendorStatus | None = Query(default=None),
    category_id: uuid.UUID | None = Query(default=None),
    sort_by: str = Query(default="created_at", pattern="^(company_name|created_at)$"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    # Vendor users can only see their own company
    if current_user.role == UserRole.VENDOR:
        if current_user.vendor_company_id is None:
            return _ok(data=PagedResponse.build([], 0, page, size).model_dump())
        svc = VendorService(db)
        vendor = await svc.get_vendor(current_user.vendor_company_id)
        return _ok(
            data=PagedResponse.build(
                [VendorResponse.model_validate(vendor).model_dump()], 1, 1, 1
            ).model_dump()
        )

    filters = VendorFilterParams(
        search=search,
        status=status,
        category_id=category_id,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    svc = VendorService(db)
    vendors, total = await svc.list_vendors(filters, page=page, size=size)
    paged = PagedResponse.build(
        items=[VendorResponse.model_validate(v).model_dump() for v in vendors],
        total=total,
        page=page,
        size=size,
    )
    return _ok(data=paged.model_dump())


# ---------------------------------------------------------------------------
# GET /vendors/{vendor_id}
# ---------------------------------------------------------------------------

@router.get("/{vendor_id}", summary="Get vendor by ID")
async def get_vendor(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    # Vendor users: only allow access to their own company
    if (
        current_user.role == UserRole.VENDOR
        and current_user.vendor_company_id != vendor_id
    ):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied.")

    svc = VendorService(db)
    vendor = await svc.get_vendor(vendor_id)
    return _ok(data=VendorResponse.model_validate(vendor).model_dump())


# ---------------------------------------------------------------------------
# POST /vendors
# ---------------------------------------------------------------------------

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new vendor")
async def create_vendor(
    payload: VendorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.PROCUREMENT_OFFICER)
    ),
) -> dict:
    svc = VendorService(db)
    vendor = await svc.create_vendor(payload, created_by_id=current_user.id)
    return _ok(
        data=VendorResponse.model_validate(vendor).model_dump(),
        message="Vendor registered successfully.",
    )


# ---------------------------------------------------------------------------
# PUT /vendors/{vendor_id}
# ---------------------------------------------------------------------------

@router.put("/{vendor_id}", summary="Update vendor details")
async def update_vendor(
    vendor_id: uuid.UUID,
    payload: VendorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.PROCUREMENT_OFFICER)
    ),
) -> dict:
    svc = VendorService(db)
    vendor = await svc.update_vendor(vendor_id, payload, updated_by_id=current_user.id)
    return _ok(
        data=VendorResponse.model_validate(vendor).model_dump(),
        message="Vendor updated successfully.",
    )


# ---------------------------------------------------------------------------
# PATCH /vendors/{vendor_id}/status
# ---------------------------------------------------------------------------

@router.patch("/{vendor_id}/status", summary="Update vendor status (approve/suspend/blacklist)")
async def update_vendor_status(
    vendor_id: uuid.UUID,
    payload: VendorStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.PROCUREMENT_OFFICER)
    ),
) -> dict:
    svc = VendorService(db)
    vendor = await svc.update_vendor_status(vendor_id, payload, updated_by_id=current_user.id)
    return _ok(
        data=VendorResponse.model_validate(vendor).model_dump(),
        message=f"Vendor status changed to '{vendor.status.value}'.",
    )


# ---------------------------------------------------------------------------
# DELETE /vendors/{vendor_id}  — soft delete (blacklist)
# ---------------------------------------------------------------------------

@router.delete("/{vendor_id}", summary="Blacklist a vendor (no hard delete, Admin only)")
async def delete_vendor(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    svc = VendorService(db)
    vendor = await svc.delete_vendor(vendor_id, updated_by_id=current_user.id)
    return _ok(
        data=VendorResponse.model_validate(vendor).model_dump(),
        message="Vendor blacklisted. Audit trail preserved.",
    )

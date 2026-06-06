"""
routers/vendor_categories.py
==============================
Vendor Category CRUD.

GET    /vendor-categories            List (active only by default)
GET    /vendor-categories/{id}       Get by ID
POST   /vendor-categories            Create (Admin/Officer)
PUT    /vendor-categories/{id}       Update (Admin/Officer)
DELETE /vendor-categories/{id}       Soft delete (Admin only)
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.vendor import VendorCategoryCreate, VendorCategoryResponse, VendorCategoryUpdate
from app.services.vendor_service import VendorCategoryService

router = APIRouter()


def _ok(data=None, message: str = "") -> dict:
    return {"success": True, "data": data, "message": message}


@router.get("/", summary="List vendor categories")
async def list_categories(
    include_inactive: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    svc = VendorCategoryService(db)
    cats = await svc.list_categories(include_inactive=include_inactive)
    return _ok(data=[VendorCategoryResponse.model_validate(c).model_dump() for c in cats])


@router.get("/{category_id}", summary="Get vendor category by ID")
async def get_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    svc = VendorCategoryService(db)
    cat = await svc.get_category(category_id)
    return _ok(data=VendorCategoryResponse.model_validate(cat).model_dump())


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create vendor category (Admin/Officer)")
async def create_category(
    payload: VendorCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.PROCUREMENT_OFFICER)
    ),
) -> dict:
    svc = VendorCategoryService(db)
    cat = await svc.create_category(payload, created_by_id=current_user.id)
    return _ok(
        data=VendorCategoryResponse.model_validate(cat).model_dump(),
        message="Category created successfully.",
    )


@router.put("/{category_id}", summary="Update vendor category (Admin/Officer)")
async def update_category(
    category_id: uuid.UUID,
    payload: VendorCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.PROCUREMENT_OFFICER)
    ),
) -> dict:
    svc = VendorCategoryService(db)
    cat = await svc.update_category(category_id, payload, updated_by_id=current_user.id)
    return _ok(
        data=VendorCategoryResponse.model_validate(cat).model_dump(),
        message="Category updated successfully.",
    )


@router.delete("/{category_id}", summary="Soft-delete vendor category (Admin only)")
async def delete_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    svc = VendorCategoryService(db)
    cat = await svc.delete_category(category_id, updated_by_id=current_user.id)
    return _ok(
        data=VendorCategoryResponse.model_validate(cat).model_dump(),
        message="Category deactivated.",
    )

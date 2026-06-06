"""
routers/users.py
================
User management endpoints — Admin only.

GET    /users            Paginated list + search
GET    /users/{id}       Get user by ID
POST   /users            Create user
PUT    /users/{id}       Update user
PATCH  /users/{id}/status  Toggle active status (soft delete)
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import require_roles
from app.models.user import User, UserRole
from app.schemas.pagination import PagedResponse
from app.schemas.user import UserCreate, UserResponse, UserStatusUpdate, UserUpdate
from app.services.user_service import UserService

router = APIRouter()

_admin_only = Depends(require_roles(UserRole.ADMIN))


def _ok(data=None, message: str = "") -> dict:
    return {"success": True, "data": data, "message": message}


# ---------------------------------------------------------------------------
# GET /users
# ---------------------------------------------------------------------------

@router.get(
    "/",
    summary="List all users (Admin only)",
    dependencies=[_admin_only],
)
async def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, description="Search by email or full name"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    svc = UserService(db)
    users, total = await svc.list_users(page=page, size=size, search=search)
    paged = PagedResponse.build(
        items=[UserResponse.model_validate(u).model_dump() for u in users],
        total=total,
        page=page,
        size=size,
    )
    return _ok(data=paged.model_dump(), message="")


# ---------------------------------------------------------------------------
# GET /users/{user_id}
# ---------------------------------------------------------------------------

@router.get(
    "/{user_id}",
    summary="Get user by ID (Admin only)",
    dependencies=[_admin_only],
)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    svc = UserService(db)
    user = await svc.get_user(user_id)
    return _ok(data=UserResponse.model_validate(user).model_dump())


# ---------------------------------------------------------------------------
# POST /users
# ---------------------------------------------------------------------------

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (Admin only)",
)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    svc = UserService(db)
    user = await svc.create_user(payload, created_by_id=admin.id)
    return _ok(
        data=UserResponse.model_validate(user).model_dump(),
        message="User created successfully.",
    )


# ---------------------------------------------------------------------------
# PUT /users/{user_id}
# ---------------------------------------------------------------------------

@router.put(
    "/{user_id}",
    summary="Update user details (Admin only)",
)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    svc = UserService(db)
    user = await svc.update_user(user_id, payload, updated_by_id=admin.id)
    return _ok(
        data=UserResponse.model_validate(user).model_dump(),
        message="User updated successfully.",
    )


# ---------------------------------------------------------------------------
# PATCH /users/{user_id}/status
# ---------------------------------------------------------------------------

@router.patch(
    "/{user_id}/status",
    summary="Activate or deactivate a user (Admin only)",
)
async def update_user_status(
    user_id: uuid.UUID,
    payload: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    svc = UserService(db)
    user = await svc.update_user_status(user_id, payload, updated_by_id=admin.id)
    state = "activated" if user.is_active else "deactivated"
    return _ok(
        data=UserResponse.model_validate(user).model_dump(),
        message=f"User {state} successfully.",
    )

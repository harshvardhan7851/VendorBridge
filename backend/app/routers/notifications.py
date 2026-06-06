"""
routers/notifications.py
========================
Notifications API endpoints under /api/v1/notifications.
"""

import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.schemas.pagination import PagedResponse
from app.services.notification_service import NotificationService

router = APIRouter()

def _ok(data=None, message: str = "") -> dict:
    return {"success": True, "data": data, "message": message}

@router.get("/", summary="List Notifications")
async def list_notifications(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    is_read: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    svc = NotificationService(db)
    notifications, total = await svc.list_notifications(
        current_user=current_user,
        is_read=is_read,
        page=page,
        size=size,
    )
    items = [NotificationResponse.model_validate(n).model_dump(mode="json") for n in notifications]
    paged = PagedResponse.build(items=items, total=total, page=page, size=size)
    return _ok(data=paged.model_dump())

@router.patch("/{notification_id}/read", summary="Mark Notification as Read")
async def mark_as_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    svc = NotificationService(db)
    notif = await svc.mark_as_read(notification_id, current_user)
    return _ok(
        data=NotificationResponse.model_validate(notif).model_dump(mode="json"),
        message="Notification marked as read."
    )

@router.patch("/read-all", summary="Mark All Notifications as Read")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    svc = NotificationService(db)
    count = await svc.mark_all_as_read(current_user)
    return _ok(message=f"{count} notification(s) marked as read.")

"""
Notifications Router — Placeholder endpoints.
"""
from uuid import UUID
from fastapi import APIRouter

router = APIRouter()
NOT_IMPLEMENTED = {"message": "Not Implemented"}


@router.get("/", summary="List My Notifications")
async def list_notifications():
    # TODO: Return notifications for the current authenticated user
    return NOT_IMPLEMENTED


@router.patch("/{notification_id}/read", summary="Mark as Read")
async def mark_notification_read(notification_id: UUID):
    # TODO: Set is_read=True for the given notification
    return NOT_IMPLEMENTED


@router.post("/mark-all-read", summary="Mark All as Read")
async def mark_all_read():
    # TODO: Bulk update all unread notifications for current user
    return NOT_IMPLEMENTED

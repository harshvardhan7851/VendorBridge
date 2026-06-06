"""
Notification Schemas — Pydantic v2 placeholders.
"""
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: UUID
    title: str
    message: str
    notification_type: str = "general"
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


class NotificationResponse(BaseModel):
    id: UUID
    title: str
    message: str
    notification_type: str
    is_read: bool
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None

    model_config = {"from_attributes": True}

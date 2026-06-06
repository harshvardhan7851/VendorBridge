"""
schemas/notification.py
=======================
Pydantic v2 schemas for Notifications.
"""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.notification import NotificationType

class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: NotificationType
    message: str
    is_read: bool
    entity_type: str | None = None
    entity_id: UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

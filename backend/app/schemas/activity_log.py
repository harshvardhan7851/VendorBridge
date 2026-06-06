"""
schemas/activity_log.py
"""
from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class ActivityLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    action: str
    entity_type: str
    entity_id: uuid.UUID
    old_values: dict | list | None
    new_values: dict | list | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

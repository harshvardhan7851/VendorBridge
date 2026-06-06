"""
services/activity_log_service.py
================================
Service for auditing and logging activity.
"""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity_log import ActivityLog

async def log_activity(
    db: AsyncSession,
    user_id: uuid.UUID,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID,
    old_values: dict | None = None,
    new_values: dict | None = None
) -> None:
    log_entry = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
    )
    db.add(log_entry)
    # We do NOT commit here. The calling service is responsible for committing 
    # the transaction so the log is atomic with the main operation.

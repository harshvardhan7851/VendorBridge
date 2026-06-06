"""
routers/activity_logs.py
"""
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.activity_log import ActivityLog
from app.schemas.pagination import PagedResponse
from app.schemas.activity_log import ActivityLogResponse

router = APIRouter()

def _ok(data=None, message=""):
    return {"success": True, "data": data, "message": message}

@router.get("/", response_model=dict)
async def list_activity_logs(
    entity_type: str = Query(None),
    user_id: uuid.UUID = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.MANAGER))
):
    query = select(ActivityLog)
    if entity_type:
        query = query.where(ActivityLog.entity_type == entity_type)
    if user_id:
        query = query.where(ActivityLog.user_id == user_id)
        
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()
    
    offset = (page - 1) * page_size
    query = query.order_by(ActivityLog.created_at.desc()).offset(offset).limit(page_size)
    
    logs = (await db.execute(query)).scalars().all()
    data = [ActivityLogResponse.model_validate(l).model_dump() for l in logs]
    return _ok(PagedResponse(items=data, total=total, page=page, size=page_size).model_dump())

@router.get("/entity/{entity_id}", response_model=dict)
async def get_activity_logs_for_entity(
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.MANAGER))
):
    query = select(ActivityLog).where(ActivityLog.entity_id == entity_id).order_by(ActivityLog.created_at.asc())
    logs = (await db.execute(query)).scalars().all()
    data = [ActivityLogResponse.model_validate(l).model_dump() for l in logs]
    return _ok(data)

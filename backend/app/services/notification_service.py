"""
services/notification_service.py
================================
Business logic for Notification management.
"""

import uuid
from fastapi import HTTPException, status
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.user import User


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_notifications(
        self,
        current_user: User,
        is_read: bool | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Notification], int]:
        query = select(Notification).where(Notification.user_id == current_user.id)

        if is_read is not None:
            query = query.where(Notification.is_read == is_read)

        # Count
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        # Paginate — newest first
        offset = (page - 1) * size
        result = await self.db.execute(
            query.order_by(Notification.created_at.desc()).offset(offset).limit(size)
        )
        notifications = list(result.scalars().all())
        return notifications, total

    async def mark_as_read(
        self, notification_id: uuid.UUID, current_user: User
    ) -> Notification:
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notif = result.scalar_one_or_none()

        if not notif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification '{notification_id}' not found.",
            )

        if notif.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied."
            )

        notif.is_read = True
        await self.db.commit()
        await self.db.refresh(notif)
        return notif

    async def mark_all_as_read(self, current_user: User) -> int:
        # Perform bulk update
        result = await self.db.execute(
            update(Notification)
            .where(Notification.user_id == current_user.id)
            .where(Notification.is_read == False)
            .values(is_read=True)
        )
        await self.db.commit()
        return result.rowcount

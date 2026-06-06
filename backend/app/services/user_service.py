"""
services/user_service.py
========================
Business logic for user management (Admin-only operations).
  - List users with pagination + search
  - Get user by ID
  - Create user
  - Update user
  - Toggle active status (soft delete / restore)
"""

import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserStatusUpdate, UserUpdate
from app.utils.security import hash_password


class UserService:
    """Admin-level user management operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # list_users
    # ------------------------------------------------------------------

    async def list_users(
        self,
        page: int = 1,
        size: int = 20,
        search: str | None = None,
    ) -> tuple[list[User], int]:
        """
        Return paginated list of users.
        Optional full-text search on email and full_name.
        Returns (items, total_count).
        """
        query = select(User)

        if search:
            term = f"%{search.lower()}%"
            query = query.where(
                or_(
                    func.lower(User.email).like(term),
                    func.lower(User.full_name).like(term),
                )
            )

        # Count total
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        # Paginate
        offset = (page - 1) * size
        result = await self.db.execute(
            query.order_by(User.created_at.desc()).offset(offset).limit(size)
        )
        users = list(result.scalars().all())

        return users, total

    # ------------------------------------------------------------------
    # get_user
    # ------------------------------------------------------------------

    async def get_user(self, user_id: uuid.UUID) -> User:
        """Fetch user by UUID. Raises 404 if not found."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user: User | None = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found.",
            )
        return user

    # ------------------------------------------------------------------
    # create_user
    # ------------------------------------------------------------------

    async def create_user(
        self,
        payload: UserCreate,
        created_by_id: uuid.UUID,
    ) -> User:
        """
        Create a new user (admin action).
        Raises 409 if email already exists.
        """
        existing = await self.db.execute(
            select(User).where(User.email == payload.email)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{payload.email}' is already registered.",
            )

        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            role=payload.role,
            phone=payload.phone,
            vendor_company_id=payload.vendor_company_id,
            updated_by=created_by_id,
            is_active=True,
            is_verified=True,   # Admin-created users are pre-verified
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # ------------------------------------------------------------------
    # update_user
    # ------------------------------------------------------------------

    async def update_user(
        self,
        user_id: uuid.UUID,
        payload: UserUpdate,
        updated_by_id: uuid.UUID,
    ) -> User:
        """Apply partial updates to an existing user."""
        user = await self.get_user(user_id)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_by = updated_by_id
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # ------------------------------------------------------------------
    # update_user_status (soft delete / restore)
    # ------------------------------------------------------------------

    async def update_user_status(
        self,
        user_id: uuid.UUID,
        payload: UserStatusUpdate,
        updated_by_id: uuid.UUID,
    ) -> User:
        """
        Toggle is_active (soft delete or restore).
        Prevents admins from deactivating themselves.
        """
        if user_id == updated_by_id and not payload.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account.",
            )

        user = await self.get_user(user_id)
        user.is_active = payload.is_active
        user.updated_by = updated_by_id
        await self.db.commit()
        await self.db.refresh(user)
        return user

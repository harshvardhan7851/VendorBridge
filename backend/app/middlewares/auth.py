"""
middlewares/auth.py
===================
FastAPI dependencies for authentication and role-based access control.

Provides:
  - get_current_user()     : Validates JWT, returns active User object.
  - require_roles(*roles)  : Role guard dependency factory.
"""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User, UserRole
from app.utils.security import decode_token

_bearer_scheme = HTTPBearer(auto_error=True)


# ---------------------------------------------------------------------------
# get_current_user
# ---------------------------------------------------------------------------

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Validates the Bearer JWT in the Authorization header.
    Returns the corresponding User from the database.

    Raises:
        401 — token missing, invalid, or expired.
        401 — user not found or deactivated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)
        token_type: str = payload.get("type", "")
        if token_type != "access":
            raise credentials_exception

        user_id_str: str | None = payload.get("sub")
        if not user_id_str:
            raise credentials_exception

        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    # Fetch user from DB
    result = await db.execute(select(User).where(User.id == user_id))
    user: User | None = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
        )

    return user


# ---------------------------------------------------------------------------
# require_roles
# ---------------------------------------------------------------------------

def require_roles(*roles: UserRole):
    """
    Dependency factory that enforces role-based access control.

    Usage:
        @router.get(
            "/admin-only",
            dependencies=[Depends(require_roles(UserRole.ADMIN))]
        )
        async def admin_only():
            ...

    Or inject the user too:
        async def endpoint(
            current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))
        ):
    """

    async def _check_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role != UserRole.ADMIN and current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied. Required role(s): "
                    f"{', '.join(r.value for r in roles)}."
                ),
            )
        return current_user

    return _check_role

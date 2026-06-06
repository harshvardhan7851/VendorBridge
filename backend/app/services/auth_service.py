"""
services/auth_service.py
=========================
Business logic for all authentication operations:
  - signup, login, refresh token, logout, get current user profile.

Architecture:
  Routers call → AuthService methods.
  AuthService performs DB queries and returns domain objects / raises HTTPExceptions.
"""

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, UserSession
from app.schemas.auth import LoginRequest, SignupRequest, TokenData
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_expiry_datetime,
    hash_password,
    verify_password,
)


class AuthService:
    """Handles all authentication lifecycle operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # signup
    # ------------------------------------------------------------------

    async def signup(self, payload: SignupRequest) -> User:
        """
        Register a new user account with role=VENDOR by default.
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
            phone=payload.phone,
            role=UserRole.VENDOR,
            is_active=True,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # ------------------------------------------------------------------
    # login
    # ------------------------------------------------------------------

    async def login(self, payload: LoginRequest) -> TokenData:
        """
        Authenticate user by email + password.
        Creates a new UserSession and returns access + refresh tokens.
        Raises 401 on bad credentials.
        """
        result = await self.db.execute(
            select(User).where(User.email == payload.email)
        )
        user: User | None = result.scalar_one_or_none()

        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated. Contact your administrator.",
            )

        # Generate tokens
        access_token = create_access_token(str(user.id), user.role.value)
        refresh_token = create_refresh_token(str(user.id))

        # Persist refresh token session
        session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=get_token_expiry_datetime(),
            is_revoked=False,
        )
        self.db.add(session)

        # Update last_login
        user.last_login = datetime.now(timezone.utc)

        await self.db.commit()

        return TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    # ------------------------------------------------------------------
    # refresh
    # ------------------------------------------------------------------

    async def refresh(self, refresh_token: str) -> TokenData:
        """
        Issue a new access token using a valid, non-revoked refresh token.
        Raises 401 if token is invalid / revoked / expired.
        """
        credentials_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise credentials_exc
            user_id = uuid.UUID(payload["sub"])
        except (JWTError, ValueError, KeyError):
            raise credentials_exc

        # Check session exists and is valid
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.refresh_token == refresh_token,
                UserSession.is_revoked == False,  # noqa: E712
                UserSession.expires_at > datetime.now(timezone.utc),
            )
        )
        session: UserSession | None = result.scalar_one_or_none()
        if not session:
            raise credentials_exc

        # Fetch user
        user_result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_active == True)  # noqa: E712
        )
        user: User | None = user_result.scalar_one_or_none()
        if not user:
            raise credentials_exc

        # Rotate: revoke old, create new
        session.is_revoked = True
        new_refresh = create_refresh_token(str(user.id))
        new_session = UserSession(
            user_id=user.id,
            refresh_token=new_refresh,
            expires_at=get_token_expiry_datetime(),
            is_revoked=False,
        )
        self.db.add(new_session)
        await self.db.commit()

        return TokenData(
            access_token=create_access_token(str(user.id), user.role.value),
            refresh_token=new_refresh,
        )

    # ------------------------------------------------------------------
    # logout
    # ------------------------------------------------------------------

    async def logout(self, refresh_token: str) -> None:
        """
        Revoke the given refresh token so it can no longer be used.
        Silent success even if token not found (prevents enumeration).
        """
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.refresh_token == refresh_token,
                UserSession.is_revoked == False,  # noqa: E712
            )
        )
        session: UserSession | None = result.scalar_one_or_none()
        if session:
            session.is_revoked = True
            await self.db.commit()

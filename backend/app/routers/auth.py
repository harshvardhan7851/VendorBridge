"""
routers/auth.py
================
Authentication endpoints.

All responses follow the standard envelope:
  {"success": true, "data": {...}, "message": "..."}
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middlewares.auth import get_current_user
from app.models.user import User
from app.schemas.auth import ApiResponse, LoginRequest, RefreshRequest, SignupRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


def _ok(data=None, message: str = "") -> dict:
    return {"success": True, "data": data, "message": message}


# ---------------------------------------------------------------------------
# POST /auth/signup
# ---------------------------------------------------------------------------

@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user (vendor self-registration)",
)
async def signup(
    payload: SignupRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    svc = AuthService(db)
    user = await svc.signup(payload)
    return _ok(
        data=UserResponse.model_validate(user).model_dump(),
        message="Account created successfully. Please log in.",
    )


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    summary="Authenticate and receive JWT tokens",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    svc = AuthService(db)
    tokens = await svc.login(payload)
    return _ok(
        data=tokens.model_dump(),
        message="Login successful.",
    )


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------

@router.post(
    "/refresh",
    summary="Exchange a refresh token for a new access token",
)
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    svc = AuthService(db)
    tokens = await svc.refresh(payload.refresh_token)
    return _ok(
        data=tokens.model_dump(),
        message="Tokens refreshed.",
    )


# ---------------------------------------------------------------------------
# POST /auth/logout
# ---------------------------------------------------------------------------

@router.post(
    "/logout",
    summary="Revoke the refresh token (server-side logout)",
)
async def logout(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    svc = AuthService(db)
    await svc.logout(payload.refresh_token)
    return _ok(message="Logged out successfully.")


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

@router.get(
    "/me",
    summary="Get the currently authenticated user's profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    return _ok(
        data=UserResponse.model_validate(current_user).model_dump(),
        message="",
    )

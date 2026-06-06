"""
utils/security.py
==================
Production security utilities:
  - Password hashing / verification (bcrypt via passlib)
  - JWT access token creation & verification
  - JWT refresh token creation & verification
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
import bcrypt

from app.core.config import settings

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """Return bcrypt hash of plain-text password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored bcrypt hash."""
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def _create_token(
    subject: str,
    token_type: str,
    extra_claims: dict[str, Any],
    expires_delta: timedelta,
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload: dict[str, Any] = {
        "sub": subject,          # user UUID as string
        "type": token_type,      # "access" | "refresh"
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: str, role: str) -> str:
    """
    Create a short-lived JWT access token.
    Claims: sub (user UUID), role, type=access.
    """
    return _create_token(
        subject=user_id,
        token_type="access",
        extra_claims={"role": role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str) -> str:
    """
    Create a long-lived JWT refresh token.
    Claims: sub (user UUID), type=refresh.
    Stored in DB (user_sessions) so it can be revoked.
    """
    return _create_token(
        subject=user_id,
        token_type="refresh",
        extra_claims={},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT token.
    Raises JWTError if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError as exc:
        raise exc


def get_token_expiry_datetime() -> datetime:
    """Return the UTC expiry datetime for a new refresh token."""
    return datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

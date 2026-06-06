"""
Auth Middleware
===============
Middleware placeholder for JWT authentication.
Verifies Bearer tokens on protected routes.
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security_scheme = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """
    Starlette middleware stub for JWT authentication.

    TODO:
      1. Extract Authorization header from request
      2. Validate "Bearer <token>" format
      3. Decode JWT using security.decode_access_token()
      4. Attach decoded user payload to request.state.user
      5. Call next(request) to proceed
      6. Raise 401 if token is missing or invalid on protected paths
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # TODO: Implement middleware logic
        await self.app(scope, receive, send)


async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = None,
):
    """
    FastAPI dependency for extracting the current user from JWT.

    TODO:
      1. Check credentials are present (raise 401 if not)
      2. Decode JWT token
      3. Fetch user from DB by subject claim
      4. Return User object
    """
    # TODO: Implement
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not implemented yet",
    )

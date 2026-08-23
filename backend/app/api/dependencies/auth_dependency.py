from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import verify_access_token
from app.schemas.auth_schema import UserContext
from app.models.user import User

from app.db.session import AsyncSessionLocal
from sqlalchemy import select

security = HTTPBearer() #This endpoint requires a Bearer token.

# Look for the Authorization header.
# Ensure it starts with Bearer.
# Extract the JWT.
# Create an HTTPAuthorizationCredentials object.

#This function may wait for I/O operations (database, network, etc.) without blocking other requests
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserContext:

    token = credentials.credentials
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identity"
        )

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(User).where(User.id == user_id)
        )

        user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,  # 403 Forbidden, identity is valid but access is denied
            detail="User account disabled"
        )

    return UserContext(
        user_id=user.id,
        username=user.username,
        role=user.role,
        department=user.department
    )
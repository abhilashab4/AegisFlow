"""
Module: Authentication Dependency (JWT + FastAPI)

Purpose:
Implements a reusable authentication dependency for protected FastAPI endpoints
using FastAPI's dependency injection system and HTTP Bearer authentication.
It validates JWT access tokens, authenticates users against the database, and
provides the authenticated user's context to route handlers.

Technical Workflow:
1. Uses HTTPBearer() to extract the JWT from the
   'Authorization: Bearer <token>' request header.
2. Verifies the JWT's signature and expiration using verify_access_token().
3. Extracts the user_id claim from the decoded token payload.
4. Creates an asynchronous SQLAlchemy session (AsyncSessionLocal) and queries
   the User table to retrieve the corresponding user record.
5. Validates that the user exists and that the account is active.
6. Raises appropriate HTTP exceptions (401 Unauthorized or 403 Forbidden)
   for invalid tokens, missing users, or disabled accounts.
7. Returns a UserContext object containing the authenticated user's details
   (user_id, username, role, and department) for authorization and business logic.

Example Usage:
@app.get("/profile")
async def get_profile(
    current_user: UserContext = Depends(get_current_user)
):
    return current_user

Authentication Flow:
Client
   │
   ▼
Bearer JWT → HTTPBearer() → JWT Verification → Database Lookup
           → User Validation → UserContext → Protected Endpoint

Benefits:
- Centralizes authentication logic in a reusable dependency.
- Prevents unauthorized access to protected API endpoints.
- Uses asynchronous database operations for improved scalability.
- Enables role-based access control (RBAC) by providing authenticated user information.
"""

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
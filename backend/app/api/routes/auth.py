from fastapi import APIRouter, HTTPException, status

from sqlalchemy import select

from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.core.security import create_access_token, verify_password
from app.db.session import AsyncSessionLocal
from app.models.user import User

from sqlalchemy import select
from app.schemas.auth_schema import RegisterRequest
from app.core.security import hash_password

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register(data: RegisterRequest):

    async with AsyncSessionLocal() as db:

        result = await db.execute(

            select(User).where(
                User.username == data.username
            )
        )

        existing_user = result.scalar_one_or_none()

        if existing_user:

            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )


        new_user = User(
            

            username=data.username,

            password_hash=hash_password(
                data.password
            ),

            role=data.role,

            department=data.department
        )

        db.add(new_user)

        await db.commit()

        await db.refresh(new_user)

        return {

            "message":
                "User registered successfully",

            "username":
                new_user.username
        }
    
@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
async def login(data: LoginRequest):

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(User).where(User.username == data.username)
        )

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if not verify_password(
            data.password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        access_token = create_access_token(
            data={
                "user_id": user.id,       
                "username": user.username,
                "role": user.role,
                "department": user.department
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
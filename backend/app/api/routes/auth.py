from fastapi import APIRouter, HTTPException, status
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.core.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

FAKE_USER_DB = {
    "admin": {
        "username": "admin",
        "role": "admin",
        "department": "compliance",
        "hashed_password": "$2b$12$ABXI8qYZaWO9uJoB5xVGm.IjPFoREepGwE5sKeu1Bhj5/g/.r6uJ."
    }
}

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
async def login(data: LoginRequest):
    user = FAKE_USER_DB.get(data.username)
    
    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": user["username"],
            "role": user["role"],
            "dept": user["department"]
        }
    )

    return {"access_token": access_token, "token_type": "bearer"}
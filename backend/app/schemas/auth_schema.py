from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserContext(BaseModel):
    user_id: str
    username: str
    role: str
    dept: str

class RegisterRequest(BaseModel):

    username: str

    password: str

    role: str = "employee"

    department: str = "general"
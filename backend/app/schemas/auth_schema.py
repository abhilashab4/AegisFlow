from pydantic import BaseModel

class LoginRequest(BaseModel):
 
    username: str
    password: str

class TokenResponse(BaseModel):
 
    access_token: str
    token_type: str

class UserContext(BaseModel):

    user_id: int
    username: str
    role: str
    department: str

class RegisterRequest(BaseModel):

    username: str
    password: str
    role: str = "employee"
    department: str = "general"
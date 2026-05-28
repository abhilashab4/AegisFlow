from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserContext(BaseModel):
    """Represents the identity and organizational context of the user."""
    username: str
    role: str
    dept: str
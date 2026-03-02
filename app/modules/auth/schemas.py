from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):    
    email: EmailStr
    password: str
    empresa_id: str
    role: Optional[str] = "user"

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    empresa_id: str

    class Config:
        from_attributes = True    
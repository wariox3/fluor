from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

from app.modules.auth.models import UserRole

class LoginRequest(BaseModel):
    email: str
    password: str
    client_type: Literal["web", "api", "integration"]

class UserInfo(BaseModel):
    id: int
    email: str
    tenant_id: int | None = None
    role: UserRole | None = None
   
class LoginResponse(BaseModel):
    access_token: str | None = None
    token_type: str | None = None
    user: UserInfo

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):    
    email: EmailStr
    password: str
    tenant_id: int | None = None
    role: UserRole = UserRole.user

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    tenant_id: int | None = None

    class Config:
        from_attributes = True    
        
class ApiKeyCreate(BaseModel):
    name: str
    tenant_id: int        
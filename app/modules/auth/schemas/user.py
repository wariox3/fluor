from pydantic import BaseModel, EmailStr
from typing import Literal

from app.modules.auth.models.user import UserRole

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

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nombres: str
    apellidos: str
    numero_identificacion: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    tenant_id: int | None = None
    nombres: str | None = None
    apellidos: str | None = None
    numero_identificacion: str | None = None
    is_verified: bool = False

    class Config:
        from_attributes = True

class RegisterResponse(BaseModel):
    user: UserResponse
    verification_link: str
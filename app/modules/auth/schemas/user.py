from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal

from app.modules.auth.models.user import UserRole

class LoginRequest(BaseModel):
    email: str
    password: str
    client_type: Literal["web", "api", "integration"]
    turnstile_token: str | None = None

class UserInfo(BaseModel):
    id: int
    email: str
    tenant_id: int | None = None
    tenant_nombre: str | None = None
    role: UserRole | None = None
    empleado_id: int | None = None
   
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
    empleado_id: int | None = None

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nombres: str
    apellidos: str
    numero_identificacion: str
    turnstile_token: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    tenant_id: int | None = None
    nombres: str | None = None
    apellidos: str | None = None
    numero_identificacion: str | None = None
    is_verified: bool = False
    empleado_id: int | None = None

    class Config:
        from_attributes = True

class RegisterResponse(BaseModel):
    user: UserResponse
    verification_link: str

class RecuperarClaveRequest(BaseModel):
    email: EmailStr
    turnstile_token: str

class RestablecerClaveRequest(BaseModel):
    token: str
    nueva_clave: str
    turnstile_token: str

class AsociarRequest(BaseModel):
    usuario_id: int
    tenant_id: int

class ReenviarVerificacionRequest(BaseModel):
    email: EmailStr
    turnstile_token: str

class PerfilResponse(BaseModel):
    nombres: str | None = None
    apellidos: str | None = None
    numero_identificacion: str | None = None
    empleado_id: int | None = None
    email: str | None = None

    class Config:
        from_attributes = True


class ActualizarPerfilRequest(BaseModel):
    nombres: str
    apellidos: str
    numero_identificacion: str

    @field_validator("nombres", "apellidos", "numero_identificacion")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío")
        return v.strip()
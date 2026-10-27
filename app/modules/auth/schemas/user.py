from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal, Optional

from app.modules.auth.models.user import UserRole

class LoginRequest(BaseModel):
    email: str
    password: str
    client_type: Literal["web", "mobile"]
    turnstile_token: str | None = None

class UserInfo(BaseModel):
    id: int
    email: str
    role: UserRole | None = None
    numero_identificacion: str | None = None

class LoginResponse(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None
    user: UserInfo

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nombres: str
    apellidos: str
    numero_identificacion: str
    turnstile_token: str | None = None

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    nombres: str | None = None
    apellidos: str | None = None
    numero_identificacion: str | None = None
    is_verified: bool = False

    class Config:
        from_attributes = True

class RegisterResponse(BaseModel):
    user: UserResponse
    verification_link: str | None = None  # solo con DEBUG; en producción va únicamente por correo

class RecuperarClaveRequest(BaseModel):
    email: EmailStr
    turnstile_token: str | None = None

class RestablecerClaveRequest(BaseModel):
    token: str
    nueva_clave: str
    turnstile_token: str | None = None

class ReenviarVerificacionRequest(BaseModel):
    email: EmailStr
    turnstile_token: str | None = None

class PerfilResponse(BaseModel):
    nombres: str | None = None
    apellidos: str | None = None
    numero_identificacion: str | None = None
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
    

class UserListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[UserResponse]        

class UserSeleccionarResponse(BaseModel):
    id: int
    email: str
    nombres: str | None = None
    apellidos: str | None = None

    class Config:
        from_attributes = True

class UserSeleccionarListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[UserSeleccionarResponse]

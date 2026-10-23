from datetime import datetime
from pydantic import BaseModel


class UserTenantAsociarRequest(BaseModel):
    tenant_id: int


class UserTenantResponse(BaseModel):
    id: int
    tenant_id: int
    tenant_nombre: str | None
    empleado_id: int | None
    codigo_usuario_fk: str | None
    activo: bool
    control: bool
    fecha_creacion: datetime


class UserTenantListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[UserTenantResponse]


class UserTenantUsuarioResponse(BaseModel):
    id: int
    usuario_id: int
    email: str
    nombres: str | None
    apellidos: str | None
    empleado_id: int | None
    codigo_usuario_fk: str | None
    activo: bool
    control: bool
    fecha_creacion: datetime


class UserTenantUsuarioListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[UserTenantUsuarioResponse]

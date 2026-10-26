from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserTenantAsociarRequest(BaseModel):
    tenant_id: int


class UserTenantActualizarRequest(BaseModel):
    """Solo se permite cambiar codigo_usuario_fk; cualquier otro campo se rechaza."""
    model_config = ConfigDict(extra="forbid")

    codigo_usuario_fk: str | None = Field(max_length=25)  # obligatorio; null o "" lo limpia

    @field_validator("codigo_usuario_fk")
    @classmethod
    def _vacio_a_none(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v or None


class UserTenantResponse(BaseModel):
    id: int
    tenant_id: int
    tenant_nombre: str | None
    empleado_id: int | None
    codigo_usuario_fk: str | None
    activo: bool
    control: bool
    erp: bool
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
    erp: bool
    fecha_creacion: datetime


class UserTenantUsuarioListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[UserTenantUsuarioResponse]

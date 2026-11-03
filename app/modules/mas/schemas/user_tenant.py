from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class UserTenantAsociarRequest(BaseModel):
    tenant_id: int


class UserTenantActualizarRequest(BaseModel):
    """Actualización parcial: solo se cambian los campos enviados; cualquier otro campo se rechaza."""
    model_config = ConfigDict(extra="forbid")

    codigo_usuario_fk: str | None = Field(default=None, max_length=25)  # null o "" lo limpia
    empleado: bool | None = None
    cliente: bool | None = None
    cliente_id: int | None = None  # null lo limpia
    codigo_operacion_fk: str | None = Field(default=None, max_length=20)  # null o "" lo limpia
    codigo_tercero_operacion_fk: int | None = None  # null lo limpia
    codigo_ciudad_origen_fk: str | None = Field(default=None, max_length=20)  # null o "" lo limpia

    @field_validator("codigo_usuario_fk", "codigo_operacion_fk", "codigo_ciudad_origen_fk")
    @classmethod
    def _vacio_a_none(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v or None

    @field_validator("empleado", "cliente")
    @classmethod
    def _bool_no_nulo(cls, v: bool | None) -> bool:
        if v is None:
            raise ValueError("no puede ser null")
        return v

    @model_validator(mode="after")
    def _al_menos_un_campo(self):
        if not self.model_fields_set:
            raise ValueError("Envía al menos un campo para actualizar")
        return self


class UserTenantResponse(BaseModel):
    id: int
    tenant_id: int
    tenant_nombre: str | None
    empleado_id: int | None
    codigo_usuario_fk: str | None
    activo: bool
    control: bool
    erp: bool
    empleado: bool
    cliente: bool
    cliente_id: int | None
    codigo_operacion_fk: str | None
    codigo_tercero_operacion_fk: int | None
    codigo_ciudad_origen_fk: str | None
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
    empleado: bool
    cliente: bool
    cliente_id: int | None
    codigo_operacion_fk: str | None
    codigo_tercero_operacion_fk: int | None
    codigo_ciudad_origen_fk: str | None
    fecha_creacion: datetime


class UserTenantUsuarioListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[UserTenantUsuarioResponse]

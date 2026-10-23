from datetime import datetime
from pydantic import BaseModel


class UserTenantResponse(BaseModel):
    id: int
    tenant_id: int
    tenant_nombre: str | None
    empleado_id: int | None
    activo: bool
    control: bool
    fecha_creacion: datetime


class UserTenantListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[UserTenantResponse]

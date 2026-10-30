from datetime import datetime
from pydantic import BaseModel, Field


class TenantDespachoCargarRequest(BaseModel):
    tenant_id: int
    codigo_despacho: int
    token_despacho: str = Field(min_length=1, max_length=20)


class TenantDespachoResponse(BaseModel):
    id: int
    fecha: datetime
    tenant_id: int
    tenant_nombre: str | None
    codigo_despacho: int

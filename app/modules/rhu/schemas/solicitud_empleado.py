from datetime import date, datetime
from pydantic import BaseModel
from typing import List, Optional


class SolicitudEmpleadoResponse(BaseModel):
    codigo_solicitud_empleado_pk: int
    codigo_empleado_fk: int
    codigo_solicitud_empleado_tipo_fk: Optional[str]
    solicitud_empleado_tipo_nombre: Optional[str]
    fecha_registro: Optional[date]
    fecha_desde: Optional[datetime]
    fecha_hasta: Optional[datetime]
    comentario: Optional[str]
    usuario: Optional[str]
    comentario_rechazo: Optional[str]
    estado_autorizado: Optional[bool]
    estado_aprobado: Optional[bool]
    estado_anulado: Optional[bool]
    estado_cerrado: Optional[bool]
    estado_solicitud: Optional[str]
    codigo_empresa_fk: int

    model_config = {"from_attributes": True}


class SolicitudEmpleadoCreate(BaseModel):
    codigo_empleado_fk: int
    codigo_solicitud_empleado_tipo_fk: str
    fecha_desde: datetime
    fecha_hasta: datetime
    comentario: Optional[str] = None


class SolicitudEmpleadoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[SolicitudEmpleadoResponse]

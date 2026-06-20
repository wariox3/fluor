from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class MonitoreoCreateRequest(BaseModel):
    codigo_vehiculo_fk: Optional[str] = None
    codigo_despacho_fk: Optional[int] = None
    codigo_ciudad_destino_fk: Optional[str] = None
    codigo_monitoreo_seguimiento_fk: Optional[int] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    fecha_ultimo_reporte: Optional[datetime] = None
    fecha_proximo_reporte: Optional[datetime] = None
    soporte: Optional[str] = None
    comentario: Optional[str] = None


class MonitoreoResponse(BaseModel):
    codigo_monitoreo_pk: int
    codigo_vehiculo_fk: Optional[str]
    codigo_despacho_fk: Optional[int]
    codigo_ciudad_destino_fk: Optional[str]
    codigo_monitoreo_seguimiento_fk: Optional[int]
    fecha_registro: Optional[datetime]
    fecha_inicio: Optional[datetime]
    fecha_fin: Optional[datetime]
    fecha_ultimo_reporte: Optional[datetime]
    fecha_proximo_reporte: Optional[datetime]
    soporte: Optional[str]
    comentario: Optional[str]
    estado_autorizado: Optional[bool]
    estado_aprobado: Optional[bool]
    estado_anulado: Optional[bool]
    estado_cerrado: Optional[bool]
    estado_terminado: Optional[bool]
    codigo_empresa_fk: int

    model_config = {"from_attributes": True}


class MonitoreoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[MonitoreoResponse]

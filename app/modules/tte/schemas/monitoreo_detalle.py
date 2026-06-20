from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class MonitoreoDetalleCreateRequest(BaseModel):
    codigo_monitoreo_fk: int
    codigo_monitoreo_seguimiento_fk: Optional[int] = None
    fecha_reporte: Optional[datetime] = None
    notificar_reporte: bool = False
    enviar_rndc: bool = False
    numero_rndc: Optional[str] = None
    comentario: Optional[str] = None


class MonitoreoDetalleResponse(BaseModel):
    codigo_monitoreo_detalle_pk: int
    codigo_monitoreo_fk: Optional[int]
    codigo_monitoreo_seguimiento_fk: Optional[int]
    fecha_registro: Optional[datetime]
    fecha_reporte: Optional[datetime]
    usuario: Optional[str]
    notificar_reporte: bool
    enviar_rndc: bool
    estado_rndc: bool
    numero_rndc: Optional[str]
    comentario: Optional[str]

    model_config = {"from_attributes": True}


class MonitoreoDetalleListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[MonitoreoDetalleResponse]

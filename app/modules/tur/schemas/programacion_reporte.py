from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProgramacionReporteResponse(BaseModel):
    codigo_programacion_reporte_pk: int
    codigo_programacion_fk: int
    fecha: Optional[datetime]
    fecha_cierre: Optional[datetime]
    reporta: Optional[str]
    comentario: Optional[str]
    cantidad_respuestas: int
    estado_autorizado: bool
    estado_aprobado: bool
    estado_anulado: bool
    estado_atendido: bool
    estado_cerrado: bool
    dia_desde: Optional[int]
    dia_hasta: Optional[int]
    codigo_programacion_reporte_tipo_fk: Optional[str]
    programacion_reporte_tipo_nombre: Optional[str]

    model_config = {"from_attributes": True}


class ProgramacionReporteListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ProgramacionReporteResponse]

class ProgramacionReporteItem(BaseModel):
    codigo_programacion_reporte_pk: int
    codigo_programacion_fk: int
    fecha: Optional[datetime]
    fecha_cierre: Optional[datetime]    
    reporta: Optional[str]
    comentario: Optional[str]
    cantidad_respuestas: int
    estado_autorizado: bool
    estado_aprobado: bool
    estado_anulado: bool
    estado_atendido: bool
    estado_cerrado: bool
    dia_desde: int
    dia_hasta: int


       
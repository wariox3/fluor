from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProgramacionReporteRespuestaResponse(BaseModel):
    codigo_programacion_reporte_respuesta_pk: int
    codigo_programacion_reporte_fk: int
    fecha: Optional[datetime]
    respuesta: Optional[str]
    usuario: Optional[str]

    model_config = {"from_attributes": True}


class ProgramacionReporteRespuestaListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ProgramacionReporteRespuestaResponse]

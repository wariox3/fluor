from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional

class ReclamoBase(BaseModel):
    codigo_empleado_fk: int

class ReclamoResponse(ReclamoBase):
    codigo_reclamo_pk: int

    class Config:
        from_attributes = True

class ReclamoResponse(BaseModel):
    codigo_reclamo_pk: int
    codigo_empleado_fk: int
    codigo_reclamo_concepto_fk: Optional[str]
    concepto_nombre: Optional[str]
    fecha: Optional[datetime]
    fecha_cierre: Optional[datetime]
    descripcion: str
    estado_autorizado: bool
    estado_aprobado: bool
    estado_anulado: bool
    estado_cerrado: bool
    estado_atendido: bool
    cantidad_respuestas: int

    model_config = {"from_attributes": True}


class ReclamoCreate(BaseModel):
    codigo_empleado_fk: int
    codigo_reclamo_concepto_fk: str
    fecha: Optional[datetime] = None
    descripcion: str

class ReclamoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ReclamoResponse]       
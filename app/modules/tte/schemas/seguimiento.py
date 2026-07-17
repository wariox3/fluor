from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SeguimientoCreateRequest(BaseModel):
    codigo_guia_fk: int
    codigo_seguimiento_tipo_fk: Optional[str] = None
    codigo_operacion_fk: Optional[str] = None
    fecha_seguimiento: Optional[datetime] = None
    comentario: Optional[str] = None
    datos: Optional[str] = None
    latitud: float = 0.0
    longitud: float = 0.0


class SeguimientoResponse(BaseModel):
    codigo_seguimiento_pk: int
    codigo_guia_fk: Optional[int]
    codigo_seguimiento_tipo_fk: Optional[str]
    codigo_operacion_fk: Optional[str]
    fecha: Optional[datetime]
    fecha_seguimiento: Optional[datetime]
    usuario: Optional[str]
    comentario: Optional[str]
    datos: Optional[str]
    estado_interface: bool
    estado_descartado: bool
    latitud: Optional[float]
    longitud: Optional[float]

    model_config = {"from_attributes": True}

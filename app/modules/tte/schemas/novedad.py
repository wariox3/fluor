from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NovedadCreateRequest(BaseModel):
    codigo_guia_fk: int
    codigo_novedad_tipo_fk: str = Field(max_length=20)
    descripcion: Optional[str] = Field(default=None, max_length=2000)
    fecha: Optional[datetime] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None


class NovedadResponse(BaseModel):
    codigo_novedad_pk: int
    codigo_novedad_tipo_fk: Optional[str]
    descripcion: Optional[str]
    solucion: Optional[str]
    fecha: Optional[datetime]
    fecha_registro: Optional[datetime]
    fecha_reporte: Optional[datetime]
    fecha_atencion: Optional[datetime]
    fecha_solucion: Optional[datetime]
    usuario: Optional[str]
    usuario_solucion: Optional[str]
    estado_reporte: Optional[bool]
    estado_atendido: Optional[bool]
    estado_solucion: Optional[bool]
    aplica_guia: Optional[bool]
    codigo_guia_fk: Optional[int]
    codigo_despacho_fk: Optional[int]
    codigo_despacho_referencia_fk: Optional[int]
    ingreso_api: bool

    model_config = {"from_attributes": True}


class NovedadListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[NovedadResponse]


class NovedadCreateResponse(NovedadResponse):
    ficheros_con_error: int = 0

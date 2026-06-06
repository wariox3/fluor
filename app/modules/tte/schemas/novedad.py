from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


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
    codigo_empresa_fk: int

    model_config = {"from_attributes": True}


class NovedadListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[NovedadResponse]

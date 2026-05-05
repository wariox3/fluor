from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class MovimientoResponse(BaseModel):
    codigo_movimiento_pk: int
    codigo_movimiento_tipo_fk: str
    codigo_movimiento_clase_fk: str
    codigo_tercero_fk: Optional[int]
    codigo_cuenta_fk: str
    codigo_empresa_fk: int
    numero: int
    fecha: date
    fecha_documento: Optional[date]
    soporte: Optional[str]
    comentarios: Optional[str]
    usuario: Optional[str]
    vr_total_bruto: Optional[float]
    vr_retencion: Optional[float]
    vr_total_neto: Optional[float]
    vr_consignacion: Optional[float]
    estado_autorizado: Optional[bool]
    estado_aprobado: Optional[bool]
    estado_anulado: Optional[bool]
    estado_contabilizado: Optional[bool]
    tercero_nombre_corto: Optional[str] = None
    movimiento_tipo_nombre: Optional[str] = None

    model_config = {"from_attributes": True}


class MovimientoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[MovimientoResponse]

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PedidoResponse(BaseModel):
    codigo_pedido_pk: int
    numero: Optional[int]
    fecha: Optional[datetime]
    codigo_pedido_tipo_fk: Optional[str]
    codigo_pedido_clase_fk: Optional[str]
    codigo_pedido_motivo_fk: Optional[str]
    codigo_clase_fk: Optional[int]
    codigo_tercero_fk: Optional[int]
    codigo_sector_fk: Optional[str]
    estado_autorizado: Optional[bool]
    estado_aprobado: Optional[bool]
    estado_anulado: Optional[bool]
    estado_contabilizado: Optional[bool]
    estado_programado: Optional[bool]
    estado_facturado: Optional[bool]
    estado_cerrado: Optional[bool]
    horas: Optional[int]
    horas_diurnas: Optional[int]
    horas_nocturnas: Optional[int]
    vr_total_precio_ajustado: Optional[float]
    vr_total_precio_minimo: Optional[float]
    vr_subtotal: Optional[float]
    vr_iva: Optional[float]
    vr_base_iva: Optional[float]
    vr_total: Optional[float]
    usuario: Optional[str]
    comentario: Optional[str]
    vr_salario_base: Optional[float]
    estrato: Optional[int]
    codigo_pedido_fk: Optional[int]
    codigo_empresa_fk: Optional[int]
    codigo_sucursal_fk: Optional[int]
    codigo_segmento_fk: Optional[str]

    model_config = {"from_attributes": True}


class PedidoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[PedidoResponse]

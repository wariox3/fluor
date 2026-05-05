from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


class FacturaResponse(BaseModel):
    codigo_factura_pk: int
    codigo_factura_tipo_fk: Optional[str]
    codigo_forma_pago_fk: Optional[str]
    codigo_factura_clase_fk: Optional[str]
    codigo_tercero_fk: Optional[int]
    codigo_sucursal_fk: Optional[int]
    codigo_empresa_fk: int
    numero: Optional[int]
    prefijo: Optional[str]
    fecha: Optional[date]
    fecha_vence: Optional[date]
    plazo_pago: Optional[int]
    soporte: Optional[str]
    orden_compra: Optional[str]
    remision: Optional[str]
    comentarios: Optional[str]
    usuario: Optional[str]
    vr_subtotal: float
    vr_subtotal_bruto: float
    vr_descuento: float
    vr_iva: Optional[float]
    vr_base_iva: Optional[float]
    vr_neto: float
    vr_total: float
    vr_retencion_fuente: float
    vr_retencion_iva: float
    vr_autoretencion: float
    vr_ica: float
    estado_autorizado: bool
    estado_aprobado: bool
    estado_anulado: bool
    estado_contabilizado: bool
    estado_electronico: Optional[bool]
    respuesta_electronico: Optional[str]
    tipo_operacion_dian: Optional[str]
    tercero_nombre_corto: Optional[str] = None
    factura_tipo_nombre: Optional[str] = None

    model_config = {"from_attributes": True}


class FacturaListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[FacturaResponse]

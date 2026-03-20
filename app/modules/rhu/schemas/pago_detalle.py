from pydantic import BaseModel
from typing import List, Optional


class PagoDetalleResponse(BaseModel):
    codigo_pago_detalle_pk: int
    codigo_concepto_fk: Optional[str]
    concepto_nombre: Optional[str]
    detalle: Optional[str]
    porcentaje: Optional[float]
    horas: Optional[float]
    dias: Optional[float]
    vr_hora: Optional[float]
    operacion: Optional[str]
    vr_pago: Optional[float]
    vr_devengado: Optional[float]
    vr_deduccion: Optional[float]
    vr_pago_operado: Optional[float]
    vr_ingreso_base_prestacion: Optional[float]
    vr_ingreso_base_cotizacion: Optional[float]

    model_config = {"from_attributes": True}


class PagoDetalleListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[PagoDetalleResponse]

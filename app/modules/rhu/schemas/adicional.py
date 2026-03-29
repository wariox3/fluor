from datetime import date
from pydantic import BaseModel
from typing import List, Optional


class AdicionalResponse(BaseModel):
    codigo_adicional_pk: int
    codigo_concepto_fk: Optional[str]
    concepto_nombre: Optional[str]
    codigo_empleado_fk: int
    empleado_nombre: Optional[str]
    codigo_adicional_periodo_fk: Optional[int]
    codigo_programacion_fk: Optional[int]
    codigo_programacion_detalle_fk: Optional[int]
    codigo_contrato_fk: Optional[int]
    codigo_soporte_contrato_fk: Optional[int]
    codigo_empresa_fk: int
    fecha: Optional[date]
    fecha_desde: Optional[date]
    fecha_hasta: Optional[date]
    vr_valor: Optional[float]
    horas: Optional[float]
    vr_hora: Optional[float]
    permanente: Optional[bool]
    aplica_dia_laborado: Optional[bool]
    aplica_dia_laborado_sin_descanso: Optional[bool]
    aplica_nomina: Optional[bool]
    aplica_prima: Optional[bool]
    aplica_cesantia: Optional[bool]
    aplica_anticipo: Optional[bool]
    detalle: Optional[str]
    detalle_interno: Optional[str]
    usuario: Optional[str]
    estado_inactivo: Optional[bool]
    estado_inactivo_periodo: Optional[bool]
    estado_autorizado: Optional[bool]
    estado_aprobado: Optional[bool]
    estado_anulado: Optional[bool]
    estado_contabilizado: Optional[bool]
    cobrar_cliente: Optional[bool]
    vr_cobrar_cliente: Optional[float]

    model_config = {"from_attributes": True}


class AdicionalListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[AdicionalResponse]

from datetime import date
from pydantic import BaseModel
from typing import List, Optional


class CreditoResponse(BaseModel):
    codigo_credito_pk: int
    codigo_credito_tipo_fk: Optional[str]
    codigo_credito_pago_tipo_fk: Optional[str]
    codigo_programacion_detalle_fk: Optional[int]
    codigo_empleado_fk: Optional[int]
    empleado_nombre: Optional[str]
    codigo_contrato_fk: Optional[int]
    codigo_grupo_fk: Optional[str]
    codigo_empresa_fk: int
    fecha: Optional[date]
    fecha_inicio: Optional[date]
    fecha_finalizacion: Optional[date]
    fecha_credito: Optional[date]
    vr_credito: Optional[float]
    vr_cuota: Optional[float]
    vr_cuota_prima: Optional[float]
    porcentaje_descuento: Optional[float]
    vr_abonos: Optional[float]
    vr_saldo: Optional[float]
    numero_cuotas: Optional[int]
    numero_cuota_actual: Optional[int]
    numero_libranza: Optional[str]
    comentario: Optional[str]
    estado_suspendido: Optional[bool]
    inactivo_periodo: Optional[bool]
    estado_pagado: Optional[bool]
    estado_autorizado: Optional[bool]
    estado_aprobado: Optional[bool]
    estado_anulado: Optional[bool]
    usuario: Optional[str]
    validar_cuotas: Optional[bool]
    aplicar_cuota_prima: Optional[bool]
    aplicar_cuota_cesantia: Optional[bool]

    model_config = {"from_attributes": True}


class CreditoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[CreditoResponse]

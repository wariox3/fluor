from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CuentaCobrarResponse(BaseModel):
    codigo_cuenta_cobrar_pk: int

    model_config = {"from_attributes": True}


class CuentaCobrarListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[CuentaCobrarResponse]

class CuentaCobrarPendienteResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List["CuentaCobrarItem"]


class CuentaCobrarItem(BaseModel):
    codigo_cuenta_cobrar_pk: int
    numero_documento: Optional[str]
    numero_referencia: Optional[str]
    fecha: Optional[datetime]
    fecha_vence: Optional[datetime]
    vr_subtotal: float	
    vr_saldo_original: float
    vr_saldo: float
    vr_saldo_operado: float
    vr_abono: float
    plazo: Optional[int]
    codigo_tercero_fk: int
    codigo_clasificacion_fk: Optional[str]
    cuenta_cobrar_tipo_nombre: Optional[str]
    tercero_nombre_corto: Optional[str]
    tercero_numero_identificacion: Optional[str]
    clasificacion_nombre: Optional[str]


       
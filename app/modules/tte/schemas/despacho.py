from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class DespachoResponse(BaseModel):
    codigo_despacho_pk: int
    numero: Optional[int]
    numero_rndc: Optional[str]

    fecha: Optional[date]
    fecha_registro: Optional[datetime]
    fecha_salida: Optional[datetime]
    fecha_llegada: Optional[datetime]
    fecha_entrega: Optional[datetime]

    codigo_operacion_fk: Optional[str]
    codigo_ciudad_origen_fk: Optional[str]
    codigo_ciudad_destino_fk: Optional[str]
    codigo_ruta_fk: Optional[str]
    codigo_cliente_fk: Optional[int]
    codigo_tercero_fk: Optional[int]
    codigo_vehiculo_fk: Optional[str]
    codigo_conductor_fk: Optional[int]
    codigo_despacho_tipo_fk: Optional[str]

    cantidad: int
    cantidad_entregada: int
    unidades: float
    peso_real: float
    peso_volumen: float

    vr_declara: float
    vr_flete: float
    vr_manejo: float
    vr_recaudo: float
    vr_flete_pago: float
    vr_anticipo: float
    vr_total: float
    vr_total_neto: float
    vr_saldo: float
    vr_costo: Optional[float]

    estado_autorizado: Optional[bool]
    estado_aprobado: Optional[bool]
    estado_cerrado: Optional[bool]
    estado_entregado: bool
    estado_anulado: Optional[bool]
    estado_liquidado: bool
    estado_soporte: Optional[bool]

    comentario: Optional[str]

    model_config = {"from_attributes": True}


class DespachoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[DespachoResponse]

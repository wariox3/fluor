from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DespachoDetalleResponse(BaseModel):
    codigo_despacho_detalle_pk: int
    codigo_despacho_fk: Optional[int]
    codigo_guia_fk: Optional[int]

    unidades: float
    peso_real: float
    peso_volumen: float
    peso_costo: float

    vr_declara: float
    vr_flete: float
    vr_manejo: float
    vr_otros: float
    vr_recaudo: float
    vr_contra_entrega: float
    vr_cobro_entrega: float
    vr_costo: Optional[float]
    vr_costo_flete: Optional[float]
    vr_costo_otros: float
    vr_costo_unidades: Optional[float]
    vr_precio_reexpedicion: float

    porcentaje_participacion_costo: float
    porcentaje_rentabilidad: float

    unidades_validacion: int
    adicional: Optional[bool]
    redespacho: bool

    model_config = {"from_attributes": True}


class DespachoDetalleListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[DespachoDetalleResponse]


class DespachoDetalleGuiaResponse(BaseModel):
    codigo_despacho_detalle_pk: int
    codigo_despacho_fk: Optional[int] = None
    numero: Optional[int] = None
    fecha_salida: Optional[datetime] = None
    estado_entregado: Optional[bool] = None
    codigo_despacho_clase_fk: Optional[str] = None
    ciudad_origen: Optional[str] = None
    ciudad_destino: Optional[str] = None
    conductor_nombre_corto: Optional[str] = None

    model_config = {"from_attributes": True}

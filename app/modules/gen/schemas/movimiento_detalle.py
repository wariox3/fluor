from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from typing import Literal

class MovimientoDetalleResponse(BaseModel):

    model_config = {"from_attributes": True}


class MovimientoDetalleListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[MovimientoDetalleResponse]

class MovimientoDetalleCreate(BaseModel):
    codigo_item_fk: Optional[int] = None
    codigo_tercero_fk: Optional[int] = None
    soporte: Optional[str] = Field(None, max_length=300)
    detalle: Optional[str] = Field(None, max_length=800)
    codigo_impuesto_retencion_fk: Optional[str] = Field(None, max_length=5)
    codigo_impuesto_industria_comercio_fk: Optional[str] = Field(None, max_length=5)
    codigo_impuesto_iva_fk: Optional[str] = Field(None, max_length=5)
    porcentaje_iva: float = 0.0
    porcentaje_descuento: float = 0.0
    cantidad: float = 0.0
    cantidad_operada: float = 0.0
    cantidad_pendiente: float = 0.0
    vr_precio: float = 0.0
    codigo_centro_costo_fk: Optional[str] = Field(None, max_length=20)
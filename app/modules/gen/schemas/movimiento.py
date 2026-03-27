from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from typing import Literal, Optional
from app.modules.gen.schemas.movimiento_detalle import MovimientoDetalleCreate, MovimientoDetalleResponse

class MovimientoResponse(BaseModel):

    model_config = {"from_attributes": True}


class MovimientoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[MovimientoResponse]

class MovimientoCreate(BaseModel):
    codigo_tercero_fk: int
    codigo_centro_costo_fk: str
    codigo_movimiento_tipo_fk: str
    codigo_resolucion_fk: Optional[int] = None
    codigo_forma_pago_fk: Optional[int] = None
    comentarios: Optional[str] = None
    orden_compra: Optional[str] = None
    soporte: Optional[str] = None
    plazo_pago: int
    fecha: datetime
    fecha_vence: date
    detalles: List[MovimientoDetalleCreate] = []
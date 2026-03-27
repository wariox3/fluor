from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from typing import Literal, Optional
from app.modules.gen.schemas.movimiento_detalle import MovimientoDetalleCreate, MovimientoDetalleResponse

class MovimientoTipoResponse(BaseModel):

    model_config = {"from_attributes": True}


class MovimientoTipoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[MovimientoTipoResponse]

class MovimientoTipoCreate(BaseModel):
    codigo_movimiento_clase_fk: str
    operacion_inventario: Literal[-1, 0, 1] = 0
    operacion_comercial: Literal[-1, 0, 1] = 0
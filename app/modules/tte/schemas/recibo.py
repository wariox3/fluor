from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class ReciboCreateRequest(BaseModel):
    codigo_recibo_tipo_fk: Optional[str] = Field(None, max_length=20)
    codigo_guia_fk: Optional[int] = None
    codigo_operacion_fk: Optional[str] = Field(None, max_length=20)
    codigo_tercero_fk: Optional[int] = None
    codigo_cliente_fk: Optional[int] = None
    numero: Optional[float] = None
    fecha: Optional[date] = None
    vr_flete: float = Field(0.0, ge=0)
    vr_manejo: float = Field(0.0, ge=0)


class ReciboResponse(BaseModel):
    codigo_recibo_pk: int
    numero: Optional[float]
    codigo_recibo_tipo_fk: Optional[str]
    codigo_guia_fk: Optional[int]
    codigo_operacion_fk: Optional[str]
    operacion_nombre: Optional[str] = None
    codigo_tercero_fk: Optional[int]
    tercero_nombre: Optional[str] = None
    codigo_cliente_fk: Optional[int]
    codigo_relacion_caja_fk: Optional[int]
    fecha: Optional[date]
    vr_flete: float
    vr_manejo: float
    vr_total: float
    estado_relacion: Optional[bool]

    model_config = {"from_attributes": True}


class ReciboListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[ReciboResponse]

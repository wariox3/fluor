from datetime import date, datetime

from pydantic import BaseModel
from typing import List, Optional

class ContratoBase(BaseModel):
    codigo_empleado_fk: int

class ContratoResponse(ContratoBase):
    codigo_contrato_pk: int

    class Config:
        from_attributes = True

class ContratoResponse(BaseModel):
    codigo_contrato_pk: int
    codigo_empleado_fk: int
    fecha_desde: Optional[date]
    fecha_hasta: Optional[date]
    vr_salario: Optional[float]

    model_config = {"from_attributes": True}


class ContratoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ContratoResponse]       
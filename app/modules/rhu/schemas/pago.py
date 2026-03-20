from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional

class PagoBase(BaseModel):
    codigo_empleado_fk: int

class PagoResponse(PagoBase):
    codigo_pago_pk: int

    class Config:
        from_attributes = True

class PagoResponse(BaseModel):
    codigo_pago_pk: int
    codigo_empleado_fk: int
    codigo_pago_tipo_fk: Optional[str]
    pago_tipo_nombre: Optional[str]
    numero: Optional[int]
    fecha_desde: Optional[datetime]
    fecha_hasta: Optional[datetime]
    vr_salario_contrato: float
    vr_devengado: float
    vr_deduccion: float
    vr_neto: float

    model_config = {"from_attributes": True}


class PagoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[PagoResponse]       
from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional

class ReclamoConceptoBase(BaseModel):
    codigo_empleado_fk: int

class ReclamoConceptoResponse(ReclamoConceptoBase):
    codigo_reclamo_concepto_pk: str
    nombre: str

    class Config:
        from_attributes = True

class ReclamoConceptoResponse(BaseModel):
    codigo_reclamo_concepto_pk: str
    nombre: str

    class Config:
        from_attributes = True


class ReclamoConceptoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ReclamoConceptoResponse]       
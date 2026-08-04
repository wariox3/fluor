from pydantic import BaseModel
from typing import List, Optional


class PuestoResponse(BaseModel):
    codigo_puesto_pk: int
    nombre: Optional[str]
    nombre_corto: Optional[str]

    model_config = {"from_attributes": True}


class PuestoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[PuestoResponse]

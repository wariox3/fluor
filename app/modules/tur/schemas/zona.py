from pydantic import BaseModel
from typing import List


class ZonaResponse(BaseModel):
    codigo_zona_pk: str
    nombre: str
    estado_inactivo: bool

    model_config = {"from_attributes": True}


class ZonaListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ZonaResponse]

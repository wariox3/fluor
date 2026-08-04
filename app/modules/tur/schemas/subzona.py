from pydantic import BaseModel
from typing import List


class SubzonaResponse(BaseModel):
    codigo_subzona_pk: str
    nombre: str
    estado_inactivo: bool

    model_config = {"from_attributes": True}


class SubzonaListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[SubzonaResponse]

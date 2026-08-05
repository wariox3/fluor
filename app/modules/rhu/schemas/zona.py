from pydantic import BaseModel
from typing import List, Optional


class ZonaResponse(BaseModel):
    codigo_zona_pk: str
    nombre: Optional[str]

    model_config = {"from_attributes": True}


class ZonaListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ZonaResponse]

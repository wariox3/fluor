from typing import List, Optional

from pydantic import BaseModel


class ZonaResponse(BaseModel):
    codigo_zona_pk: str
    nombre: Optional[str]

    model_config = {"from_attributes": True}


class ZonaListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ZonaResponse]

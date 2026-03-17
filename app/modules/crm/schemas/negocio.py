from pydantic import BaseModel
from typing import List, Optional


class NegocioResponse(BaseModel):
    codigo_negocio_pk: int
    nombre: Optional[str] = None

    model_config = {"from_attributes": True}


class NegocioListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[NegocioResponse]
       
from typing import List, Optional

from pydantic import BaseModel


class EmpaqueResponse(BaseModel):
    codigo_empaque_pk: str
    nombre: Optional[str]

    model_config = {"from_attributes": True}


class EmpaqueListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[EmpaqueResponse]

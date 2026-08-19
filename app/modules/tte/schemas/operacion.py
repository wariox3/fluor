from typing import List, Optional

from pydantic import BaseModel


class OperacionResponse(BaseModel):
    codigo_operacion_pk: str
    nombre: Optional[str]

    model_config = {"from_attributes": True}


class OperacionListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[OperacionResponse]

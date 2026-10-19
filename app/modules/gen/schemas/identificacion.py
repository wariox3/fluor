from pydantic import BaseModel
from typing import Optional


class IdentificacionResponse(BaseModel):
    codigo_identificacion_pk: str
    nombre: Optional[str] = None

    model_config = {"from_attributes": True}


class IdentificacionListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[IdentificacionResponse]

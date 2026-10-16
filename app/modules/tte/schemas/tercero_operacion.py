from typing import Optional

from pydantic import BaseModel, Field


class TerceroOperacionCreateRequest(BaseModel):
    codigo_tercero_fk: int
    codigo: Optional[str] = Field(None, max_length=20)
    nombre: Optional[str] = Field(None, max_length=150)


class TerceroOperacionResponse(BaseModel):
    codigo_tercero_operacion_pk: int
    codigo_tercero_fk: int
    tercero_nombre: Optional[str] = None
    codigo: Optional[str] = None
    nombre: Optional[str] = None

    model_config = {"from_attributes": True}


class TerceroOperacionListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[TerceroOperacionResponse]

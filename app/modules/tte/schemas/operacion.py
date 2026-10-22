from typing import Optional

from pydantic import BaseModel


class OperacionResponse(BaseModel):
    codigo_operacion_pk: str
    nombre: Optional[str]

    model_config = {"from_attributes": True}


class OperacionDetalleResponse(OperacionResponse):
    codigo_ciudad_fk: Optional[str] = None
    codigo_operacion_cargo_fk: Optional[str] = None
    codigo_operacion_grupo_fk: Optional[str] = None
    codigo_tercero_fk: Optional[int] = None
    codigo_centro_costo_fk: Optional[str] = None
    cola_rotulo: Optional[str] = None
    retencion_industria_comercio: Optional[bool] = None


class OperacionListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[OperacionResponse]

from pydantic import BaseModel
from typing import Optional


class PuestoResponse(BaseModel):
    codigo_puesto_pk: int
    nombre: Optional[str]
    nombre_corto: Optional[str]
    zona_nombre: Optional[str]
    subzona_nombre: Optional[str]
    area_nombre: Optional[str]
    subarea_nombre: Optional[str]

    model_config = {"from_attributes": True}


class PuestoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[PuestoResponse]

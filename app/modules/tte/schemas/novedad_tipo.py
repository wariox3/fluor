from typing import Optional

from pydantic import BaseModel


class NovedadTipoResponse(BaseModel):
    codigo_novedad_tipo_pk: str
    nombre: Optional[str]
    interna: Optional[bool]
    aplica_movil: Optional[bool]
    codigo_interface: Optional[str]

    model_config = {"from_attributes": True}


class NovedadTipoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[NovedadTipoResponse]

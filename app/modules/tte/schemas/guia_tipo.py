from typing import Optional

from pydantic import BaseModel


class GuiaTipoResponse(BaseModel):
    codigo_guia_tipo_pk: str
    nombre: Optional[str]

    model_config = {"from_attributes": True}


class GuiaTipoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[GuiaTipoResponse]

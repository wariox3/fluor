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


class GuiaTipoDescargarResponse(BaseModel):
    codigo_guia_tipo_pk: str
    nombre: Optional[str]
    codigo_pago_fk: Optional[str] = None
    codigo_forma_pago: Optional[str] = None
    validar_flete: Optional[bool] = None
    genera_cobro: Optional[bool] = None

    model_config = {"from_attributes": True}

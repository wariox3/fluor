from typing import Optional

from pydantic import BaseModel


class UsuarioConfiguracionResponse(BaseModel):
    username_pk: str
    porcentaje_manejo_minimo: Optional[float] = None
    manejo_minimo_unidad: Optional[float] = None
    manejo_minimo_despacho: Optional[float] = None
    descuento_peso_maximo: Optional[float] = None
    restringir_guia_nueva: Optional[bool] = None
    cambiar_valores_guia: bool

    model_config = {"from_attributes": True}


class UsuarioConfiguracionListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[UsuarioConfiguracionResponse]

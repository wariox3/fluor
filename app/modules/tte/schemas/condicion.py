from typing import Optional

from pydantic import BaseModel


class CondicionResponse(BaseModel):
    codigo_condicion_pk: int
    nombre: Optional[str] = None
    codigo_precio_fk: Optional[int] = None
    precio_general: Optional[bool] = None
    precio_peso: Optional[bool] = None
    precio_unidad: Optional[bool] = None
    precio_adicional: Optional[bool] = None

    model_config = {"from_attributes": True}


class CondicionListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[CondicionResponse]


class CondicionBuscarResponse(BaseModel):
    codigo_condicion_pk: int
    nombre: Optional[str] = None

    model_config = {"from_attributes": True}


class CondicionBuscarListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[CondicionBuscarResponse]


class CondicionDetalleResponse(CondicionResponse):
    peso_minimo: Optional[int] = None
    peso_minimo_guia: Optional[int] = None
    porcentaje_manejo: Optional[float] = None
    manejo_minimo_unidad: Optional[float] = None
    manejo_minimo_despacho: Optional[float] = None
    descuento_peso: Optional[float] = None
    descuento_unidad: Optional[float] = None
    limitar_descuento_reexpedicion: Optional[bool] = None
    comentario: Optional[str] = None

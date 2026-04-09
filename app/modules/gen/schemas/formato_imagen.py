from pydantic import BaseModel
from typing import List, Optional


class FormatoImagenResponse(BaseModel):
    codigo_formato_imagen_pk: int
    codigo_formato_fk: int
    posicion_x: Optional[int] = None
    posicion_y: Optional[int] = None
    ancho: Optional[int] = None
    alto: Optional[int] = None
    extension: Optional[str] = None
    visualizar_ultima_pagina: Optional[bool] = None

    model_config = {"from_attributes": True}


class FormatoImagenListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[FormatoImagenResponse]

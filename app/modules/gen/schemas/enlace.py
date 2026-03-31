from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class EnlaceResponse(BaseModel):
    codigo_enlace_pk: int
    codigo_modelo_fk: Optional[str] = None
    codigo_documento: Optional[int] = None
    url: Optional[str] = None
    nombre: Optional[str] = None
    usuario: Optional[str] = None
    descripcion: Optional[str] = None
    fecha: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EnlaceListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[EnlaceResponse]

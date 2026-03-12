from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class FicheroResponse(BaseModel):
    codigo_fichero_pk: int
    codigo_fichero_tipo_fk: str
    codigo_modelo_fk: str
    codigo: str
    fecha: Optional[datetime]
    nombre: str
    extension: str
    tipo: str
    ui: str
    comprimido: bool
    tamano: float
    usuario: str
    directorio_base: str
    error_carga: bool



    model_config = {"from_attributes": True}


class FicheroListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[FicheroResponse]
       
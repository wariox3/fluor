from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class FicheroResponse(BaseModel):
    codigo_fichero_pk: int
    codigo_fichero_tipo_fk: str
    codigo_modelo_fk: str
    codigo: str
    fecha: Optional[datetime]
    nombre: Optional[str]
    extension: Optional[str]
    tipo: Optional[str]
    ui: Optional[str]
    comprimido: Optional[bool]
    tamano: Optional[float]
    usuario: Optional[str]
    directorio_base: Optional[str]
    error_carga: Optional[bool]



    model_config = {"from_attributes": True}


class FicheroListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[FicheroResponse]
       
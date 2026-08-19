from typing import List, Optional

from pydantic import BaseModel


class CiudadResponse(BaseModel):
    codigo_ciudad_pk: str
    nombre: Optional[str]
    codigo_departamento_fk: Optional[str]
    codigo_interface: Optional[str]
    codigo_general: Optional[str]
    estado_inactivo: Optional[bool]
    codigo_ruta_fk: Optional[str] = None
    ruta_nombre: Optional[str] = None

    model_config = {"from_attributes": True}


class CiudadListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[CiudadResponse]

from pydantic import BaseModel
from typing import List, Optional


class AsesorResponse(BaseModel):
    codigo_asesor_pk: int
    numero_identificacion: str
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    celular: Optional[str] = None
    email: Optional[str] = None
    estado_inactivo: bool = False

    model_config = {"from_attributes": True}


class AsesorListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[AsesorResponse]

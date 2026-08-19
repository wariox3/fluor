from typing import List, Optional

from pydantic import BaseModel


class ServicioResponse(BaseModel):
    codigo_servicio_pk: str
    nombre: Optional[str]

    model_config = {"from_attributes": True}


class ServicioListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ServicioResponse]

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ReclamoRespuestaResponse(BaseModel):
    codigo_reclamo_respuesta_pk: int
    codigo_reclamo_fk: int
    fecha: Optional[datetime]
    respuesta: Optional[str]

    model_config = {"from_attributes": True}


class ReclamoRespuestaListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ReclamoRespuestaResponse]

from pydantic import BaseModel
from typing import Optional


class RegimenDescargarResponse(BaseModel):
    codigo_regimen_pk: str
    nombre: Optional[str] = None

    model_config = {"from_attributes": True}

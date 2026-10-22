from pydantic import BaseModel
from typing import Optional


class TipoPersonaDescargarResponse(BaseModel):
    codigo_tipo_persona_pk: str
    nombre: Optional[str] = None

    model_config = {"from_attributes": True}

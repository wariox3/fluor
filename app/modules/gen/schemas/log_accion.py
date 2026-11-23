from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class LogAccionResponse(BaseModel):
    codigo_log_accion_pk: int
    fecha: datetime
    codigo_modelo_fk: str
    codigo_registro: int
    accion: str
    usuario: str
    campos: Optional[dict[str, Any]] = None

    model_config = {"from_attributes": True}


class LogAccionListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[LogAccionResponse]

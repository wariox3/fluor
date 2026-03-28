from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class NotificacionCreate(BaseModel):
    usuario_id: int
    tipo: str
    titulo: str
    mensaje: Optional[str] = None
    url: Optional[str] = None


class NotificacionResponse(BaseModel):
    id: int
    tipo: str
    titulo: str
    mensaje: Optional[str]
    url: Optional[str]
    leida: bool
    fecha_creacion: datetime

    model_config = {"from_attributes": True}


class NotificacionListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[NotificacionResponse]


class ContadorResponse(BaseModel):
    no_leidas: int

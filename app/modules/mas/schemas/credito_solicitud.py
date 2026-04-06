from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class UsuarioResumen(BaseModel):
    id: int
    email: str
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    numero_identificacion: Optional[str] = None

    model_config = {"from_attributes": True}


class CreditoSolicitudResponse(BaseModel):
    codigo_credito_solicitud_pk: int
    usuario_id: int
    monto: Decimal
    plazo: int
    tasa_interes: Optional[Decimal] = None
    descripcion: Optional[str] = None
    estado: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    model_config = {"from_attributes": True}


class CreditoSolicitudDetalleResponse(CreditoSolicitudResponse):
    usuario: Optional[UsuarioResumen] = None


class CreditoSolicitudListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[CreditoSolicitudResponse]


class CreditoSolicitudCrear(BaseModel):
    monto: Decimal
    plazo: int
    descripcion: str


class CreditoSolicitudActualizarEstado(BaseModel):
    estado: str  # pendiente, aprobado, rechazado, desembolsado

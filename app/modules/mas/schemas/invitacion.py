from datetime import datetime
from pydantic import BaseModel
from app.modules.mas.models.invitacion import EstadoInvitacion


class InvitacionCreate(BaseModel):
    usuario_invitado_id: int
    tenant_id: int


class InvitacionResponse(BaseModel):
    id: int
    tenant_id: int
    usuario_id: int | None
    usuario_invitado_id: int
    estado: EstadoInvitacion
    fecha: datetime

    model_config = {"from_attributes": True}


class InvitacionPendienteResponse(BaseModel):
    id: int
    tenant_id: int
    tenant_nombre: str | None
    usuario_id: int | None
    usuario_nombre: str | None
    usuario_email: str | None
    fecha: datetime


class InvitacionPendienteListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[InvitacionPendienteResponse]

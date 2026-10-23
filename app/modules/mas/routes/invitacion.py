from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session
from app.core.master_database import get_master_db
from app.core.rate_limit import limiter
from app.core.security import get_current_user_from_token
from app.modules.mas.models.invitacion import EstadoInvitacion
from app.modules.mas.schemas.invitacion import (
    InvitacionCreate,
    InvitacionPendienteListResponse,
    InvitacionResponse,
    InvitacionTenantListResponse,
)
from app.modules.mas.services import invitacion as invitacion_service

router = APIRouter()


@router.post("/nuevo", response_model=InvitacionResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
@limiter.limit("10/minute")
def nuevo(
    request: Request,
    response: Response,
    data: InvitacionCreate,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    return invitacion_service.crear(db, int(current_user["sub"]), data.tenant_id, data.usuario_invitado_id)


@router.get("/pendientes", response_model=InvitacionPendienteListResponse, include_in_schema=False)
def pendientes(
    page: int = 1,
    size: int = 50,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    total, items = invitacion_service.listar_pendientes(db, int(current_user["sub"]), page, size)
    return InvitacionPendienteListResponse(total=total, page=page, size=size, items=items)


@router.get("/lista", response_model=InvitacionTenantListResponse, include_in_schema=False)
def lista(
    tenant_id: int,
    estado: EstadoInvitacion | None = None,
    page: int = 1,
    size: int = 50,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """Invitaciones de una empresa, filtrables por estado. Solo para quien es control activo en ella."""
    total, items = invitacion_service.listar_tenant(db, int(current_user["sub"]), tenant_id, estado, page, size)
    return InvitacionTenantListResponse(total=total, page=page, size=size, items=items)


@router.post("/{invitacion_id}/aceptar", response_model=InvitacionResponse, include_in_schema=False)
def aceptar(
    invitacion_id: int,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    return invitacion_service.aceptar(db, invitacion_id, int(current_user["sub"]))


@router.post("/{invitacion_id}/rechazar", response_model=InvitacionResponse, include_in_schema=False)
def rechazar(
    invitacion_id: int,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    return invitacion_service.rechazar(db, invitacion_id, int(current_user["sub"]))

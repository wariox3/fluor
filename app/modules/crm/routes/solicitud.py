"""
PQRS (solicitudes) del portal de clientes.

Reemplaza las APIs de holmio que consumía terbio (`Cliente/Crm/SolicitudContorller`):
- `/crm/api/gestion/solicitud/lista` → `GET /lista-portal`

El cliente solo ve las solicitudes registradas a su nombre (`crm_solicitud.codigo_tercero_fk`).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.crm.models.solicitud import Solicitud
from app.modules.crm.schemas.solicitud import SolicitudPortalListResponse

router = APIRouter()


def _query_portal(db: Session, tercero_id: int):
    """Solicitudes del cliente, con su tipo y su canal."""
    return (
        db.query(Solicitud)
        .options(
            joinedload(Solicitud.solicitud_tipo_rel),
            joinedload(Solicitud.tercero_rel),
            joinedload(Solicitud.canal_rel),
        )
        .filter(Solicitud.codigo_tercero_fk == tercero_id)
    )


@router.get("/lista-portal", response_model=SolicitudPortalListResponse)
def lista_portal(
    tercero_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = _query_portal(db, tercero_id)

    total = query.with_entities(func.count(Solicitud.codigo_solicitud_pk)).scalar()
    offset = (page - 1) * size
    items = (
        query
        # Como holmio, de la más reciente a la más antigua
        .order_by(Solicitud.codigo_solicitud_pk.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    return SolicitudPortalListResponse(total=total, page=page, size=size, items=items)

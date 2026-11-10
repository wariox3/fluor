"""
Cotizaciones del portal de clientes.

Reemplaza las APIs de holmio que consumía terbio (`Cliente/Crm/CotizacionController`):
- `/crm/api/comercial/cotizacion/lista` → `GET /lista-portal`

El cliente solo ve las cotizaciones registradas a su nombre (`crm_cotizacion.codigo_tercero_fk`).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.crm.models.cotizacion import Cotizacion
from app.modules.crm.schemas.cotizacion import CotizacionPortalListResponse

router = APIRouter()


def _query_portal(db: Session, tercero_id: int):
    """Cotizaciones del cliente, con su tipo, asesor, forma de pago y negocio."""
    return (
        db.query(Cotizacion)
        .options(
            joinedload(Cotizacion.cotizacion_tipo_rel),
            joinedload(Cotizacion.tercero_rel),
            joinedload(Cotizacion.asesor_rel),
            joinedload(Cotizacion.forma_pago_rel),
            joinedload(Cotizacion.negocio_rel),
        )
        .filter(Cotizacion.codigo_tercero_fk == tercero_id)
    )


@router.get("/lista-portal", response_model=CotizacionPortalListResponse)
def lista_portal(
    tercero_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = _query_portal(db, tercero_id)

    total = query.with_entities(func.count(Cotizacion.codigo_cotizacion_pk)).scalar()
    offset = (page - 1) * size
    items = (
        query
        # Como holmio, de la más reciente a la más antigua
        .order_by(Cotizacion.codigo_cotizacion_pk.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    return CotizacionPortalListResponse(total=total, page=page, size=size, items=items)

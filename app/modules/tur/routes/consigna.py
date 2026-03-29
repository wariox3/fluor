from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.consigna import Consigna
from app.modules.tur.schemas.consigna import ConsignaListResponse

router = APIRouter()


@router.get("/lista", response_model=ConsignaListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    puesto_id: Optional[int] = None,
    habilitado_portal: Optional[bool] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Consigna).options(joinedload(Consigna.puesto_rel))

    if puesto_id:
        query = query.filter(Consigna.codigo_puesto_fk == puesto_id)
    if habilitado_portal is not None:
        query = query.filter(Consigna.habilitado_portal == habilitado_portal)

    total = query.with_entities(func.count(Consigna.codigo_consigna_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(Consigna.codigo_consigna_pk.asc()).offset(offset).limit(size).all()

    return ConsignaListResponse(total=total, page=page, size=size, items=items)

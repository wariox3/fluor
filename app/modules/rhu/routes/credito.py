from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.credito import Credito
from app.modules.rhu.schemas.credito import CreditoListResponse

router = APIRouter()


@router.get("/lista", response_model=CreditoListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    empleado_id: Optional[int] = None,
    estado_pagado: Optional[bool] = None,
    estado_anulado: Optional[bool] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Credito).options(joinedload(Credito.empleado_rel))

    if empleado_id:
        query = query.filter(Credito.codigo_empleado_fk == empleado_id)
    if estado_pagado is not None:
        query = query.filter(Credito.estado_pagado == estado_pagado)
    if estado_anulado is not None:
        query = query.filter(Credito.estado_anulado == estado_anulado)

    total = query.with_entities(func.count(Credito.codigo_credito_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(Credito.codigo_credito_pk.desc()).offset(offset).limit(size).all()

    return CreditoListResponse(total=total, page=page, size=size, items=items)

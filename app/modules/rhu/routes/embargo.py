from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.embargo import Embargo
from app.modules.rhu.schemas.embargo import EmbargoListResponse

router = APIRouter()


@router.get("/lista", response_model=EmbargoListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    empleado_id: Optional[int] = None,
    estado_activo: Optional[bool] = None,
    estado_anulado: Optional[bool] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Embargo).options(joinedload(Embargo.empleado_rel))

    if empleado_id:
        query = query.filter(Embargo.codigo_empleado_fk == empleado_id)
    if estado_activo is not None:
        query = query.filter(Embargo.estado_activo == estado_activo)
    if estado_anulado is not None:
        query = query.filter(Embargo.estado_anulado == estado_anulado)

    total = query.with_entities(func.count(Embargo.codigo_embargo_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(Embargo.codigo_embargo_pk.desc()).offset(offset).limit(size).all()

    return EmbargoListResponse(total=total, page=page, size=size, items=items)

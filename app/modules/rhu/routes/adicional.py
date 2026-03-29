from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.adicional import Adicional
from app.modules.rhu.schemas.adicional import AdicionalListResponse

router = APIRouter()


@router.get("/lista", response_model=AdicionalListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    empleado_id: Optional[int] = None,
    estado_inactivo: Optional[bool] = None,
    estado_anulado: Optional[bool] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Adicional).options(
        joinedload(Adicional.empleado_rel),
        joinedload(Adicional.concepto_rel),
    )

    if empleado_id:
        query = query.filter(Adicional.codigo_empleado_fk == empleado_id)
    if estado_inactivo is not None:
        query = query.filter(Adicional.estado_inactivo == estado_inactivo)
    if estado_anulado is not None:
        query = query.filter(Adicional.estado_anulado == estado_anulado)

    total = query.with_entities(func.count(Adicional.codigo_adicional_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(Adicional.codigo_adicional_pk.desc()).offset(offset).limit(size).all()

    return AdicionalListResponse(total=total, page=page, size=size, items=items)

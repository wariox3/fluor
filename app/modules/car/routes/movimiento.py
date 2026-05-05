from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from datetime import date
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.car.models.movimiento import Movimiento
from app.modules.car.schemas.movimiento import MovimientoListResponse

router = APIRouter()


@router.get("/lista", response_model=MovimientoListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    tercero_id: Optional[int] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Movimiento)
    if tercero_id:
        query = query.filter(Movimiento.codigo_tercero_fk == tercero_id)
    if fecha_desde:
        query = query.filter(Movimiento.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Movimiento.fecha <= fecha_hasta)
    total = query.with_entities(func.count(Movimiento.codigo_movimiento_pk)).scalar()
    offset = (page - 1) * size
    movimientos = (
        query
        .options(joinedload(Movimiento.tercero), joinedload(Movimiento.movimiento_tipo))
        .order_by(Movimiento.codigo_movimiento_pk.desc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return MovimientoListResponse(total=total, page=page, size=size, items=movimientos)

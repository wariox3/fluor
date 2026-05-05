from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from datetime import date
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.factura import Factura
from app.modules.tur.schemas.factura import FacturaListResponse

router = APIRouter()


@router.get("/lista", response_model=FacturaListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    tercero_id: Optional[int] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Factura)
    if tercero_id:
        query = query.filter(Factura.codigo_tercero_fk == tercero_id)
    if fecha_desde:
        query = query.filter(Factura.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Factura.fecha <= fecha_hasta)
    total = query.with_entities(func.count(Factura.codigo_factura_pk)).scalar()
    offset = (page - 1) * size
    facturas = (
        query
        .options(joinedload(Factura.tercero), joinedload(Factura.factura_tipo))
        .order_by(Factura.codigo_factura_pk.desc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return FacturaListResponse(total=total, page=page, size=size, items=facturas)

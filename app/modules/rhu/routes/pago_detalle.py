from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.pago_detalle import PagoDetalle
from app.modules.rhu.schemas.pago_detalle import PagoDetalleListResponse

router = APIRouter()


@router.get("/lista", response_model=PagoDetalleListResponse)
def lista(pago_id: int, page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = (
        db.query(PagoDetalle)
        .options(joinedload(PagoDetalle.concepto))
        .filter(PagoDetalle.codigo_pago_fk == pago_id)
        .order_by(PagoDetalle.codigo_concepto_fk)
    )
    total = query.with_entities(func.count(PagoDetalle.codigo_pago_detalle_pk)).scalar()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return PagoDetalleListResponse(total=total, page=page, size=size, items=items)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.pago import Pago
from app.modules.rhu.schemas.pago import PagoListResponse

router = APIRouter()


@router.get("/lista", response_model=PagoListResponse)
def lista(page: int = 1, size: int = 50, numero_identificacion: Optional[str] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Pago)
    if numero_identificacion:
        query = query.filter(Pago.codigo_empleado_fk == numero_identificacion)
    total = query.with_entities(func.count(Pago.codigo_pago_pk)).scalar()
    offset = (page - 1) * size
    pagos = query.offset(offset).limit(size).all()
    return PagoListResponse(total=total, page=page, size=size, items=pagos)
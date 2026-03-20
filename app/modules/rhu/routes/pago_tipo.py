from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.pago_tipo import PagoTipo
from app.modules.rhu.schemas.pago_tipo import PagoTipoListResponse

router = APIRouter()


@router.get("/lista", response_model=PagoTipoListResponse)
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(PagoTipo)
    total = query.with_entities(func.count(PagoTipo.codigo_pago_tipo_pk)).scalar()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return PagoTipoListResponse(total=total, page=page, size=size, items=items)

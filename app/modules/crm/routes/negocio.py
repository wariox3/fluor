from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.crm.models.negocio import Negocio
from app.modules.crm.schemas.negocio import NegocioListResponse

router = APIRouter()

@router.get("/lista", response_model=NegocioListResponse)
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    total = db.query(func.count(Negocio.codigo_negocio_pk)).scalar()
    offset = (page - 1) * size
    negocios = (
        db.query(Negocio)
        .offset(offset)
        .limit(size)
        .all()
    )
    return NegocioListResponse(total=total, page=page, size=size, items=negocios)
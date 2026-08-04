from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.puesto import Puesto
from app.modules.tur.schemas.puesto import PuestoListResponse

router = APIRouter()


@router.get("/lista", response_model=PuestoListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    puesto_id: Optional[int] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Puesto).options(joinedload(Puesto.zona_rel), joinedload(Puesto.subzona_rel))
    if puesto_id:
        query = query.filter(Puesto.codigo_puesto_pk == puesto_id)
    total = query.with_entities(func.count(Puesto.codigo_puesto_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(Puesto.nombre).offset(offset).limit(size).all()
    return PuestoListResponse(total=total, page=page, size=size, items=items)

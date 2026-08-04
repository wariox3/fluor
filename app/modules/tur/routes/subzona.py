from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.subzona import TurSubzona
from app.modules.tur.schemas.subzona import SubzonaListResponse

router = APIRouter()


@router.get("/lista", response_model=SubzonaListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    subzona_id: Optional[str] = None,
    nombre: Optional[str] = None,
    estado_inactivo: Optional[bool] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(TurSubzona)
    if subzona_id:
        query = query.filter(TurSubzona.codigo_subzona_pk == subzona_id)
    if nombre:
        query = query.filter(TurSubzona.nombre.ilike(f"%{nombre}%"))
    if estado_inactivo is not None:
        query = query.filter(TurSubzona.estado_inactivo == estado_inactivo)
    total = query.with_entities(func.count(TurSubzona.codigo_subzona_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(TurSubzona.nombre).offset(offset).limit(size).all()
    return SubzonaListResponse(total=total, page=page, size=size, items=items)

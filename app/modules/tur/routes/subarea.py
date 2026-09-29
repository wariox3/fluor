from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.subarea import TurSubarea
from app.modules.tur.schemas.subarea import SubareaListResponse

router = APIRouter()


@router.get("/lista", response_model=SubareaListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    subarea_id: Optional[str] = None,
    nombre: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(TurSubarea)
    if subarea_id:
        query = query.filter(TurSubarea.codigo_subarea_pk == subarea_id)
    if nombre:
        query = query.filter(TurSubarea.nombre.ilike(f"%{nombre}%"))
    total = query.with_entities(func.count(TurSubarea.codigo_subarea_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(TurSubarea.nombre).offset(offset).limit(size).all()
    return SubareaListResponse(total=total, page=page, size=size, items=items)

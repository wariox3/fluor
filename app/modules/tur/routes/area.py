from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.area import TurArea
from app.modules.tur.schemas.area import AreaListResponse

router = APIRouter()


@router.get("/lista", response_model=AreaListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    area_id: Optional[str] = None,
    nombre: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(TurArea)
    if area_id:
        query = query.filter(TurArea.codigo_area_pk == area_id)
    if nombre:
        query = query.filter(TurArea.nombre.ilike(f"%{nombre}%"))
    total = query.with_entities(func.count(TurArea.codigo_area_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(TurArea.nombre).offset(offset).limit(size).all()
    return AreaListResponse(total=total, page=page, size=size, items=items)

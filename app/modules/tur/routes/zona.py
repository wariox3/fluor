from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.zona import TurZona
from app.modules.tur.schemas.zona import ZonaListResponse

router = APIRouter()


@router.get("/lista", response_model=ZonaListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    zona_id: Optional[str] = None,
    nombre: Optional[str] = None,
    estado_inactivo: Optional[bool] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(TurZona)
    if zona_id:
        query = query.filter(TurZona.codigo_zona_pk == zona_id)
    if nombre:
        query = query.filter(TurZona.nombre.ilike(f"%{nombre}%"))
    if estado_inactivo is not None:
        query = query.filter(TurZona.estado_inactivo == estado_inactivo)
    total = query.with_entities(func.count(TurZona.codigo_zona_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(TurZona.nombre).offset(offset).limit(size).all()
    return ZonaListResponse(total=total, page=page, size=size, items=items)

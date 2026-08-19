from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.zona import Zona
from app.modules.tte.schemas.zona import ZonaListResponse

router = APIRouter()


@router.get("/buscar", response_model=ZonaListResponse)
def buscar(
    page: int = 1,
    size: int = 50,
    pk: Optional[str] = None,
    nombre: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Zona)

    if pk:
        query = query.filter(Zona.codigo_zona_pk == pk)
    if nombre:
        query = query.filter(Zona.nombre.ilike(f"%{nombre}%"))

    total = query.with_entities(func.count(Zona.codigo_zona_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(Zona.nombre.asc()).offset(offset).limit(size).all()

    return ZonaListResponse(total=total, page=page, size=size, items=items)

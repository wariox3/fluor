from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.servicio import Servicio
from app.modules.tte.schemas.servicio import ServicioListResponse

router = APIRouter()


@router.get("/buscar", response_model=ServicioListResponse)
def buscar(
    page: int = 1,
    size: int = 50,
    pk: Optional[str] = None,
    nombre: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Servicio)

    if pk:
        query = query.filter(Servicio.codigo_servicio_pk == pk)
    if nombre:
        query = query.filter(Servicio.nombre.ilike(f"%{nombre}%"))

    total = query.with_entities(func.count(Servicio.codigo_servicio_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(Servicio.nombre.asc()).offset(offset).limit(size).all()

    return ServicioListResponse(total=total, page=page, size=size, items=items)

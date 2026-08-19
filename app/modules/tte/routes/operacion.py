from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.operacion import Operacion
from app.modules.tte.schemas.operacion import OperacionListResponse

router = APIRouter()


@router.get("/buscar", response_model=OperacionListResponse)
def buscar(
    page: int = 1,
    size: int = 50,
    pk: Optional[str] = None,
    nombre: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Operacion)

    if pk:
        query = query.filter(Operacion.codigo_operacion_pk == pk)
    if nombre:
        query = query.filter(Operacion.nombre.ilike(f"%{nombre}%"))

    total = query.with_entities(func.count(Operacion.codigo_operacion_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(Operacion.nombre.asc()).offset(offset).limit(size).all()

    return OperacionListResponse(total=total, page=page, size=size, items=items)

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.producto import Producto
from app.modules.tte.schemas.producto import ProductoListResponse

router = APIRouter()


@router.get("/buscar", response_model=ProductoListResponse)
def buscar(
    page: int = 1,
    size: int = 50,
    pk: Optional[str] = None,
    nombre: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Producto)

    if pk:
        query = query.filter(Producto.codigo_producto_pk == pk)
    if nombre:
        query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))

    total = query.with_entities(func.count(Producto.codigo_producto_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(Producto.nombre.asc()).offset(offset).limit(size).all()

    return ProductoListResponse(total=total, page=page, size=size, items=items)

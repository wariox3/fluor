from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.tercero_producto import TerceroProducto
from app.modules.tte.schemas.tercero_producto import TerceroProductoListResponse

router = APIRouter()


@router.get("/buscar", response_model=TerceroProductoListResponse)
def buscar(
    codigo_tercero_fk: int,
    page: int = 1,
    size: int = 50,
    pk: Optional[int] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(TerceroProducto).filter(TerceroProducto.codigo_tercero_fk == codigo_tercero_fk)

    if pk is not None:
        query = query.filter(TerceroProducto.codigo_tercero_producto_pk == pk)

    total = query.with_entities(func.count(TerceroProducto.codigo_tercero_producto_pk)).scalar()
    offset = (page - 1) * size
    items = (
        query.options(joinedload(TerceroProducto.tercero), joinedload(TerceroProducto.producto))
        .order_by(TerceroProducto.codigo_tercero_producto_pk.asc())
        .offset(offset)
        .limit(size)
        .all()
    )

    return TerceroProductoListResponse(total=total, page=page, size=size, items=items)

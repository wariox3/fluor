from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.cliente_condicion import ClienteCondicion
from app.modules.tte.schemas.cliente_condicion import ClienteCondicionListResponse

router = APIRouter()


@router.get("/buscar", response_model=ClienteCondicionListResponse)
def buscar(
    page: int = 1,
    size: int = 50,
    pk: Optional[int] = None,
    codigo_tercero_fk: Optional[int] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(ClienteCondicion)

    if pk is not None:
        query = query.filter(ClienteCondicion.codigo_cliente_condicion_pk == pk)
    if codigo_tercero_fk is not None:
        query = query.filter(ClienteCondicion.codigo_tercero_fk == codigo_tercero_fk)

    total = query.with_entities(func.count(ClienteCondicion.codigo_cliente_condicion_pk)).scalar()
    offset = (page - 1) * size
    items = (
        query.options(joinedload(ClienteCondicion.tercero), joinedload(ClienteCondicion.condicion))
        .order_by(ClienteCondicion.codigo_cliente_condicion_pk.asc())
        .offset(offset)
        .limit(size)
        .all()
    )

    return ClienteCondicionListResponse(total=total, page=page, size=size, items=items)

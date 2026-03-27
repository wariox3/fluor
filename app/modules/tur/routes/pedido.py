from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.pedido import Pedido
from app.modules.tur.schemas.pedido import PedidoListResponse

router = APIRouter()


@router.get("/lista", response_model=PedidoListResponse)
def lista(page: int = 1, size: int = 50, tercero_id: Optional[int] = None, fecha_desde: Optional[date] = None, fecha_hasta: Optional[date] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user),):
    query = db.query(Pedido)
    if tercero_id:
        query = query.filter(Pedido.codigo_tercero_fk == tercero_id)
    if fecha_desde:
        query = query.filter(Pedido.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Pedido.fecha <= fecha_hasta)
    total = query.with_entities(func.count(Pedido.codigo_pedido_pk)).scalar()
    offset = (page - 1) * size
    pedidos = query.order_by(Pedido.codigo_pedido_pk.desc()).offset(offset).limit(size).all()
    return PedidoListResponse(total=total, page=page, size=size, items=pedidos)

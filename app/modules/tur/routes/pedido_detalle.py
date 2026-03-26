from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.pedido_detalle import PedidoDetalle
from app.modules.tur.models.pedido import Pedido
from app.modules.tur.schemas.pedido_detalle import PedidoDetalleListResponse

router = APIRouter()


@router.get("/lista", response_model=PedidoDetalleListResponse)
def lista(page: int = 1, size: int = 50, pedido_detalle_id: Optional[int] = None, tercero_id: Optional[int] = None, anio: Optional[int] = None, mes: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user),):
    query = db.query(PedidoDetalle)
    if pedido_detalle_id:
        query = query.filter(PedidoDetalle.codigo_pedido_detalle_pk == pedido_detalle_id)
    if tercero_id:
        query = query.join(Pedido, Pedido.codigo_pedido_pk == PedidoDetalle.codigo_pedido_fk)
        query = query.filter(Pedido.codigo_tercero_fk == tercero_id)
    if anio:
        query = query.filter(PedidoDetalle.anio == anio)
    if mes:
        query = query.filter(PedidoDetalle.mes == mes)
    total = query.with_entities(func.count(PedidoDetalle.codigo_pedido_detalle_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(PedidoDetalle.codigo_pedido_detalle_pk.desc()).offset(offset).limit(size).all()
    return PedidoDetalleListResponse(total=total, page=page, size=size, items=items)

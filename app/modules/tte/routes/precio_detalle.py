from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.precio import Precio
from app.modules.tte.models.precio_detalle import PrecioDetalle
from app.modules.tte.models.producto import Producto
from app.modules.tte.models.zona import Zona
from app.modules.tte.schemas.precio_detalle import PrecioDetalleListResponse, PrecioDetalleProductoClienteResponse

router = APIRouter()


@router.get("/lista", response_model=PrecioDetalleListResponse)
def lista(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    codigo_precio_fk: Optional[int] = None,
    codigo_ciudad_origen_fk: Optional[str] = None,
    codigo_ciudad_destino_fk: Optional[str] = None,
    codigo_zona_fk: Optional[str] = None,
    codigo_producto_fk: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(PrecioDetalle)
    if codigo_precio_fk is not None:
        query = query.filter(PrecioDetalle.codigo_precio_fk == codigo_precio_fk)
    if codigo_ciudad_origen_fk is not None:
        query = query.filter(PrecioDetalle.codigo_ciudad_origen_fk == codigo_ciudad_origen_fk)
    if codigo_ciudad_destino_fk is not None:
        query = query.filter(PrecioDetalle.codigo_ciudad_destino_fk == codigo_ciudad_destino_fk)
    if codigo_zona_fk is not None:
        query = query.filter(PrecioDetalle.codigo_zona_fk == codigo_zona_fk)
    if codigo_producto_fk is not None:
        query = query.filter(PrecioDetalle.codigo_producto_fk == codigo_producto_fk)
    total = query.with_entities(func.count(PrecioDetalle.codigo_precio_detalle_pk)).scalar()

    ciudad_origen = aliased(Ciudad)
    ciudad_destino = aliased(Ciudad)
    offset = (page - 1) * size
    items = (
        query.outerjoin(Precio, PrecioDetalle.codigo_precio_fk == Precio.codigo_precio_pk)
        .outerjoin(ciudad_origen, PrecioDetalle.codigo_ciudad_origen_fk == ciudad_origen.codigo_ciudad_pk)
        .outerjoin(ciudad_destino, PrecioDetalle.codigo_ciudad_destino_fk == ciudad_destino.codigo_ciudad_pk)
        .outerjoin(Zona, PrecioDetalle.codigo_zona_fk == Zona.codigo_zona_pk)
        .outerjoin(Producto, PrecioDetalle.codigo_producto_fk == Producto.codigo_producto_pk)
        .with_entities(
            PrecioDetalle.codigo_precio_detalle_pk,
            PrecioDetalle.codigo_precio_fk,
            Precio.omitir_descuento,
            PrecioDetalle.codigo_ciudad_origen_fk,
            ciudad_origen.nombre.label("ciudad_origen_nombre"),
            PrecioDetalle.codigo_ciudad_destino_fk,
            ciudad_destino.nombre.label("ciudad_destino_nombre"),
            PrecioDetalle.codigo_zona_fk,
            Zona.nombre.label("zona_nombre"),
            PrecioDetalle.codigo_producto_fk,
            Producto.nombre.label("producto_nombre"),
            PrecioDetalle.codigo_cobertura_fk,
            PrecioDetalle.vr_peso,
            PrecioDetalle.vr_unidad,
            PrecioDetalle.peso_tope,
            PrecioDetalle.vr_peso_tope,
            PrecioDetalle.vr_peso_tope_adicional,
            PrecioDetalle.minimo,
        )
        .order_by(PrecioDetalle.codigo_precio_detalle_pk.asc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return PrecioDetalleListResponse(total=total, page=page, size=size, items=items)


@router.get(
    "/producto-cliente",
    response_model=list[PrecioDetalleProductoClienteResponse],
    description="Productos distintos que usa una lista de precios.",
)
def producto_cliente(
    codigo_precio_fk: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    return (
        db.query(Producto.codigo_producto_pk, Producto.nombre)
        .join(PrecioDetalle, PrecioDetalle.codigo_producto_fk == Producto.codigo_producto_pk)
        .filter(PrecioDetalle.codigo_precio_fk == codigo_precio_fk)
        .distinct()
        .order_by(Producto.nombre.asc(), Producto.codigo_producto_pk.asc())
        .all()
    )

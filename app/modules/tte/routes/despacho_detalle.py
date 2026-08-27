from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased
from typing import List, Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.conductor import Conductor
from app.modules.tte.models.despacho import Despacho
from app.modules.tte.models.despacho_detalle import DespachoDetalle
from app.modules.tte.schemas.despacho_detalle import (
    DespachoDetalleResponse,
    DespachoDetalleListResponse,
    DespachoDetalleGuiaResponse,
)

router = APIRouter()


@router.get("/lista", response_model=DespachoDetalleListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    codigo_despacho_fk: Optional[int] = None,
    codigo_guia_fk: Optional[int] = None,
    adicional: Optional[bool] = None,
    redespacho: Optional[bool] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(DespachoDetalle)
    if codigo_despacho_fk is not None:
        query = query.filter(DespachoDetalle.codigo_despacho_fk == codigo_despacho_fk)
    if codigo_guia_fk is not None:
        query = query.filter(DespachoDetalle.codigo_guia_fk == codigo_guia_fk)
    if adicional is not None:
        query = query.filter(DespachoDetalle.adicional == adicional)
    if redespacho is not None:
        query = query.filter(DespachoDetalle.redespacho == redespacho)

    total = query.with_entities(func.count(DespachoDetalle.codigo_despacho_detalle_pk)).scalar()
    offset = (page - 1) * size
    detalles = query.order_by(DespachoDetalle.codigo_despacho_detalle_pk.desc()).offset(offset).limit(size).all()
    return DespachoDetalleListResponse(total=total, page=page, size=size, items=detalles)


@router.get("/detalle/{codigo_despacho_detalle_pk}", response_model=DespachoDetalleResponse)
def detalle(codigo_despacho_detalle_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    despacho_detalle = db.query(DespachoDetalle).filter(DespachoDetalle.codigo_despacho_detalle_pk == codigo_despacho_detalle_pk).first()

    if not despacho_detalle:
        raise HTTPException(status_code=404, detail="Despacho detalle no encontrado")

    return despacho_detalle


@router.get("/guia/{codigo_guia_fk}", response_model=List[DespachoDetalleGuiaResponse])
def guia(codigo_guia_fk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    ciudad_origen = aliased(Ciudad)
    ciudad_destino = aliased(Ciudad)

    query = (
        db.query(
            DespachoDetalle,
            Despacho.numero.label("numero"),
            Despacho.fecha_salida.label("fecha_salida"),
            Despacho.estado_entregado.label("estado_entregado"),
            Despacho.codigo_despacho_clase_fk.label("codigo_despacho_clase_fk"),
            ciudad_origen.nombre.label("ciudad_origen"),
            ciudad_destino.nombre.label("ciudad_destino"),
            Conductor.nombre_corto.label("conductor_nombre_corto"),
        )
        .join(Despacho, DespachoDetalle.codigo_despacho_fk == Despacho.codigo_despacho_pk)
        .outerjoin(ciudad_origen, Despacho.codigo_ciudad_origen_fk == ciudad_origen.codigo_ciudad_pk)
        .outerjoin(ciudad_destino, Despacho.codigo_ciudad_destino_fk == ciudad_destino.codigo_ciudad_pk)
        .outerjoin(Conductor, Despacho.codigo_conductor_fk == Conductor.codigo_conductor_pk)
        .filter(DespachoDetalle.codigo_guia_fk == codigo_guia_fk, Despacho.estado_anulado == False)
    )

    rows = query.order_by(Despacho.fecha_registro).all()
    items = []
    for detalle, numero, fecha_salida, estado_entregado, codigo_despacho_clase_fk, ciudad_origen_nombre, ciudad_destino_nombre, conductor_nombre_corto in rows:
        item = DespachoDetalleGuiaResponse.model_validate(detalle)
        item.numero = numero
        item.fecha_salida = fecha_salida
        item.estado_entregado = estado_entregado
        item.codigo_despacho_clase_fk = codigo_despacho_clase_fk
        item.ciudad_origen = ciudad_origen_nombre
        item.ciudad_destino = ciudad_destino_nombre
        item.conductor_nombre_corto = conductor_nombre_corto
        items.append(item)
    return items

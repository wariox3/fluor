from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.despacho import Despacho
from app.modules.tte.schemas.despacho import (
    DespachoResponse,
    DespachoListResponse,
)

router = APIRouter()


@router.get("/lista", response_model=DespachoListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    numero: Optional[int] = None,
    codigo_operacion_fk: Optional[str] = None,
    codigo_ciudad_origen_fk: Optional[str] = None,
    codigo_ciudad_destino_fk: Optional[str] = None,
    codigo_ruta_fk: Optional[str] = None,
    codigo_cliente_fk: Optional[int] = None,
    codigo_tercero_fk: Optional[int] = None,
    codigo_vehiculo_fk: Optional[str] = None,
    codigo_conductor_fk: Optional[int] = None,
    codigo_despacho_tipo_fk: Optional[str] = None,
    estado_entregado: Optional[bool] = None,
    estado_cerrado: Optional[bool] = None,
    estado_liquidado: Optional[bool] = None,
    estado_anulado: Optional[bool] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Despacho)
    if numero is not None:
        query = query.filter(Despacho.numero == numero)
    if codigo_operacion_fk is not None:
        query = query.filter(Despacho.codigo_operacion_fk == codigo_operacion_fk)
    if codigo_ciudad_origen_fk is not None:
        query = query.filter(Despacho.codigo_ciudad_origen_fk == codigo_ciudad_origen_fk)
    if codigo_ciudad_destino_fk is not None:
        query = query.filter(Despacho.codigo_ciudad_destino_fk == codigo_ciudad_destino_fk)
    if codigo_ruta_fk is not None:
        query = query.filter(Despacho.codigo_ruta_fk == codigo_ruta_fk)
    if codigo_cliente_fk is not None:
        query = query.filter(Despacho.codigo_cliente_fk == codigo_cliente_fk)
    if codigo_tercero_fk is not None:
        query = query.filter(Despacho.codigo_tercero_fk == codigo_tercero_fk)
    if codigo_vehiculo_fk is not None:
        query = query.filter(Despacho.codigo_vehiculo_fk == codigo_vehiculo_fk)
    if codigo_conductor_fk is not None:
        query = query.filter(Despacho.codigo_conductor_fk == codigo_conductor_fk)
    if codigo_despacho_tipo_fk is not None:
        query = query.filter(Despacho.codigo_despacho_tipo_fk == codigo_despacho_tipo_fk)
    if estado_entregado is not None:
        query = query.filter(Despacho.estado_entregado == estado_entregado)
    if estado_cerrado is not None:
        query = query.filter(Despacho.estado_cerrado == estado_cerrado)
    if estado_liquidado is not None:
        query = query.filter(Despacho.estado_liquidado == estado_liquidado)
    if estado_anulado is not None:
        query = query.filter(Despacho.estado_anulado == estado_anulado)
    if fecha_desde is not None:
        query = query.filter(Despacho.fecha >= fecha_desde)
    if fecha_hasta is not None:
        query = query.filter(Despacho.fecha <= fecha_hasta)

    total = query.with_entities(func.count(Despacho.codigo_despacho_pk)).scalar()
    offset = (page - 1) * size
    despachos = query.order_by(Despacho.codigo_despacho_pk.desc()).offset(offset).limit(size).all()
    return DespachoListResponse(total=total, page=page, size=size, items=despachos)


@router.get("/detalle/{codigo_despacho_pk}", response_model=DespachoResponse)
def detalle(codigo_despacho_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    despacho = db.query(Despacho).filter(Despacho.codigo_despacho_pk == codigo_despacho_pk).first()

    if not despacho:
        raise HTTPException(status_code=404, detail="Despacho no encontrado")

    return despacho

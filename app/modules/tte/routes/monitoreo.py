from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.core.config import DEFAULT_EMPRESA_ID
from app.modules.tte.models.monitoreo import Monitoreo
from app.modules.tte.schemas.monitoreo import (
    MonitoreoCreateRequest,
    MonitoreoResponse,
    MonitoreoListResponse,
)

router = APIRouter()


@router.post("/nuevo", response_model=MonitoreoResponse)
def nuevo(payload: MonitoreoCreateRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    monitoreo = Monitoreo(
        codigo_vehiculo_fk=payload.codigo_vehiculo_fk,
        codigo_despacho_fk=payload.codigo_despacho_fk,
        codigo_ciudad_destino_fk=payload.codigo_ciudad_destino_fk,
        codigo_monitoreo_seguimiento_fk=payload.codigo_monitoreo_seguimiento_fk,
        fecha_registro=datetime.now(),
        fecha_inicio=payload.fecha_inicio,
        fecha_fin=payload.fecha_fin,
        fecha_ultimo_reporte=payload.fecha_ultimo_reporte,
        fecha_proximo_reporte=payload.fecha_proximo_reporte,
        soporte=payload.soporte,
        comentario=payload.comentario,
        codigo_empresa_fk=DEFAULT_EMPRESA_ID,
    )

    db.add(monitoreo)
    db.commit()
    db.refresh(monitoreo)

    return monitoreo


@router.get("/lista", response_model=MonitoreoListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    codigo_vehiculo_fk: Optional[str] = None,
    codigo_despacho_fk: Optional[int] = None,
    codigo_monitoreo_seguimiento_fk: Optional[int] = None,
    estado_cerrado: Optional[bool] = None,
    estado_terminado: Optional[bool] = None,
    estado_anulado: Optional[bool] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Monitoreo)
    if codigo_vehiculo_fk is not None:
        query = query.filter(Monitoreo.codigo_vehiculo_fk == codigo_vehiculo_fk)
    if codigo_despacho_fk is not None:
        query = query.filter(Monitoreo.codigo_despacho_fk == codigo_despacho_fk)
    if codigo_monitoreo_seguimiento_fk is not None:
        query = query.filter(Monitoreo.codigo_monitoreo_seguimiento_fk == codigo_monitoreo_seguimiento_fk)
    if estado_cerrado is not None:
        query = query.filter(Monitoreo.estado_cerrado == estado_cerrado)
    if estado_terminado is not None:
        query = query.filter(Monitoreo.estado_terminado == estado_terminado)
    if estado_anulado is not None:
        query = query.filter(Monitoreo.estado_anulado == estado_anulado)
    if fecha_desde is not None:
        query = query.filter(Monitoreo.fecha_registro >= fecha_desde)
    if fecha_hasta is not None:
        query = query.filter(Monitoreo.fecha_registro <= fecha_hasta)
    total = query.with_entities(func.count(Monitoreo.codigo_monitoreo_pk)).scalar()
    offset = (page - 1) * size
    monitoreos = query.order_by(Monitoreo.codigo_monitoreo_pk.desc()).offset(offset).limit(size).all()
    return MonitoreoListResponse(total=total, page=page, size=size, items=monitoreos)


@router.get("/detalle/{codigo_monitoreo_pk}", response_model=MonitoreoResponse)
def detalle(codigo_monitoreo_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    monitoreo = db.query(Monitoreo).filter(Monitoreo.codigo_monitoreo_pk == codigo_monitoreo_pk).first()

    if not monitoreo:
        raise HTTPException(status_code=404, detail="Monitoreo no encontrado")

    return monitoreo

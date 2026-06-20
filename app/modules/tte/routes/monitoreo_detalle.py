from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.monitoreo import Monitoreo
from app.modules.tte.models.monitoreo_detalle import MonitoreoDetalle
from app.modules.tte.schemas.monitoreo_detalle import (
    MonitoreoDetalleCreateRequest,
    MonitoreoDetalleResponse,
    MonitoreoDetalleListResponse,
)

router = APIRouter()


@router.post("/nuevo", response_model=MonitoreoDetalleResponse)
def nuevo(payload: MonitoreoDetalleCreateRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    monitoreo = db.query(Monitoreo).filter(Monitoreo.codigo_monitoreo_pk == payload.codigo_monitoreo_fk).first()
    if not monitoreo:
        raise HTTPException(status_code=404, detail="Monitoreo no encontrado")

    detalle = MonitoreoDetalle(
        codigo_monitoreo_fk=payload.codigo_monitoreo_fk,
        codigo_monitoreo_seguimiento_fk=payload.codigo_monitoreo_seguimiento_fk,
        fecha_registro=datetime.now(),
        fecha_reporte=payload.fecha_reporte,
        usuario=str(current_user["sub"]),
        notificar_reporte=payload.notificar_reporte,
        enviar_rndc=payload.enviar_rndc,
        numero_rndc=payload.numero_rndc,
        comentario=payload.comentario,
    )

    # El último reporte del detalle actualiza el seguimiento del monitoreo
    monitoreo.fecha_ultimo_reporte = detalle.fecha_reporte or detalle.fecha_registro
    if payload.codigo_monitoreo_seguimiento_fk is not None:
        monitoreo.codigo_monitoreo_seguimiento_fk = payload.codigo_monitoreo_seguimiento_fk

    db.add(detalle)
    db.commit()
    db.refresh(detalle)

    return detalle


@router.get("/lista", response_model=MonitoreoDetalleListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    codigo_monitoreo_fk: Optional[int] = None,
    codigo_monitoreo_seguimiento_fk: Optional[int] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(MonitoreoDetalle)
    if codigo_monitoreo_fk is not None:
        query = query.filter(MonitoreoDetalle.codigo_monitoreo_fk == codigo_monitoreo_fk)
    if codigo_monitoreo_seguimiento_fk is not None:
        query = query.filter(MonitoreoDetalle.codigo_monitoreo_seguimiento_fk == codigo_monitoreo_seguimiento_fk)
    total = query.with_entities(func.count(MonitoreoDetalle.codigo_monitoreo_detalle_pk)).scalar()
    offset = (page - 1) * size
    detalles = query.order_by(MonitoreoDetalle.codigo_monitoreo_detalle_pk.desc()).offset(offset).limit(size).all()
    return MonitoreoDetalleListResponse(total=total, page=page, size=size, items=detalles)

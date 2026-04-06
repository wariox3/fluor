from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Optional
from app.core.master_database import get_master_db
from app.core.security import get_current_user
from app.modules.mas.models.credito_solicitud import CreditoSolicitud
from app.modules.mas.schemas.credito_solicitud import (
    CreditoSolicitudListResponse,
    CreditoSolicitudResponse,
    CreditoSolicitudDetalleResponse,
    CreditoSolicitudCrear,
    CreditoSolicitudActualizarEstado,
)

router = APIRouter()


@router.get("/lista", response_model=CreditoSolicitudListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    estado: Optional[str] = None,
    usuario_id: Optional[int] = None,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(CreditoSolicitud)
    if estado:
        query = query.filter(CreditoSolicitud.estado == estado)
    if usuario_id:
        query = query.filter(CreditoSolicitud.usuario_id == usuario_id)
    total = query.with_entities(func.count(CreditoSolicitud.codigo_credito_solicitud_pk)).scalar()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return CreditoSolicitudListResponse(total=total, page=page, size=size, items=items)


@router.get("/{id}", response_model=CreditoSolicitudDetalleResponse)
def detalle(
    id: int,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    solicitud = db.query(CreditoSolicitud).filter(CreditoSolicitud.codigo_credito_solicitud_pk == id).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return solicitud


@router.post("/nuevo", response_model=CreditoSolicitudResponse, status_code=201)
def nuevo(
    datos: CreditoSolicitudCrear,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    solicitud = CreditoSolicitud(
        usuario_id=int(current_user["sub"]),
        monto=datos.monto,
        plazo=datos.plazo,
        descripcion=datos.descripcion,
        tasa_interes=0,
        estado="pendiente",
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud



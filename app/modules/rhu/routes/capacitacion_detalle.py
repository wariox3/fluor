from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.capacitacion_detalle import CapacitacionDetalle
from app.modules.rhu.schemas.capacitacion_detalle import CapacitacionDetalleListResponse

router = APIRouter()


@router.get("/lista", response_model=CapacitacionDetalleListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    capacitacion_id: Optional[int] = None,
    empleado_id: Optional[int] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(CapacitacionDetalle).options(joinedload(CapacitacionDetalle.capacitacion_rel))

    if capacitacion_id:
        query = query.filter(CapacitacionDetalle.codigo_capacitacion_fk == capacitacion_id)
    if empleado_id:
        query = query.filter(CapacitacionDetalle.codigo_empleado_fk == empleado_id)

    total = query.with_entities(func.count(CapacitacionDetalle.codigo_capacitacion_detalle_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(CapacitacionDetalle.codigo_capacitacion_detalle_pk.desc()).offset(offset).limit(size).all()

    return CapacitacionDetalleListResponse(total=total, page=page, size=size, items=items)


@router.get("/lista-portal", response_model=CapacitacionDetalleListResponse)
def lista_portal(
    empleado_id: int,
    page: int = 1,
    size: int = 50,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(CapacitacionDetalle).options(joinedload(CapacitacionDetalle.capacitacion_rel)).filter(
        CapacitacionDetalle.codigo_empleado_fk == empleado_id,
        CapacitacionDetalle.asistencia == False,
    )

    total = query.with_entities(func.count(CapacitacionDetalle.codigo_capacitacion_detalle_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(CapacitacionDetalle.codigo_capacitacion_detalle_pk.desc()).offset(offset).limit(size).all()

    return CapacitacionDetalleListResponse(total=total, page=page, size=size, items=items)


@router.post("/confirmar-asistencia/{capacitacion_detalle_id}")
def confirmar_asistencia(
    capacitacion_detalle_id: int,
    request: Request,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    detalle = db.query(CapacitacionDetalle).filter(
        CapacitacionDetalle.codigo_capacitacion_detalle_pk == capacitacion_detalle_id
    ).first()

    if not detalle:
        raise HTTPException(status_code=404, detail="Capacitacion detalle no encontrado")

    if detalle.asistencia:
        raise HTTPException(status_code=400, detail="La asistencia ya fue confirmada previamente")

    detalle.asistencia = True
    detalle.ip_confirmacion_usuario = request.client.host
    detalle.fecha_confirmacion_usuario = datetime.now()
    db.commit()

    return {"detail": "Asistencia confirmada"}

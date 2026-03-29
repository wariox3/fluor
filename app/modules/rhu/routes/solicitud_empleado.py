from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.core.config import DEFAULT_EMPRESA_ID
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.models.solicitud_empleado import SolicitudEmpleado
from app.modules.rhu.models.solicitud_empleado_tipo import SolicitudEmpleadoTipo
from app.modules.rhu.schemas.solicitud_empleado import SolicitudEmpleadoCreate, SolicitudEmpleadoListResponse, SolicitudEmpleadoResponse

router = APIRouter()


@router.post("/nuevo", response_model=SolicitudEmpleadoResponse)
def nuevo(
    data: SolicitudEmpleadoCreate,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    empleado = db.query(Empleado).filter(Empleado.codigo_empleado_pk == data.codigo_empleado_fk).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if data.codigo_solicitud_empleado_tipo_fk:
        tipo = db.query(SolicitudEmpleadoTipo).filter(
            SolicitudEmpleadoTipo.codigo_solicitud_empleado_tipo_pk == data.codigo_solicitud_empleado_tipo_fk
        ).first()
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de solicitud no encontrado")

    solicitud = SolicitudEmpleado(
        codigo_empleado_fk=data.codigo_empleado_fk,
        codigo_solicitud_empleado_tipo_fk=data.codigo_solicitud_empleado_tipo_fk,
        fecha_registro=date.today(),
        fecha_desde=data.fecha_desde,
        fecha_hasta=data.fecha_hasta,
        comentario=data.comentario,
        usuario="portal",
        codigo_empresa_fk=DEFAULT_EMPRESA_ID,
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud


@router.get("/lista", response_model=SolicitudEmpleadoListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    empleado_id: Optional[int] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(SolicitudEmpleado).options(joinedload(SolicitudEmpleado.solicitud_empleado_tipo))
    if empleado_id:
        query = query.filter(SolicitudEmpleado.codigo_empleado_fk == empleado_id)
    total = query.with_entities(func.count(SolicitudEmpleado.codigo_solicitud_empleado_pk)).scalar()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return SolicitudEmpleadoListResponse(total=total, page=page, size=size, items=items)

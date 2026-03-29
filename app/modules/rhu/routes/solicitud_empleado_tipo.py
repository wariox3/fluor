from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.solicitud_empleado_tipo import SolicitudEmpleadoTipo
from app.modules.rhu.schemas.solicitud_empleado_tipo import SolicitudEmpleadoTipoListResponse

router = APIRouter()


@router.get("/lista", response_model=SolicitudEmpleadoTipoListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    nombre: str = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(SolicitudEmpleadoTipo).filter(SolicitudEmpleadoTipo.habilitado_portal == True)
    if nombre:
        query = query.filter(SolicitudEmpleadoTipo.nombre.ilike(f"%{nombre}%"))
    total = query.with_entities(func.count(SolicitudEmpleadoTipo.codigo_solicitud_empleado_tipo_pk)).scalar()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return SolicitudEmpleadoTipoListResponse(total=total, page=page, size=size, items=items)

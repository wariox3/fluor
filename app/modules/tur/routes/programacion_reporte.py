from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.programacion import Programacion
from app.modules.tur.models.programacion_reporte import ProgramacionReporte
from app.modules.tur.schemas.programacion_reporte import ProgramacionReporteListResponse

router = APIRouter()


@router.get("/lista", response_model=ProgramacionReporteListResponse)
def lista(page: int = 1, size: int = 50, empleado_id: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = (
        db.query(ProgramacionReporte)
        .join(Programacion, ProgramacionReporte.codigo_programacion_fk == Programacion.codigo_programacion_pk)
        .options(joinedload(ProgramacionReporte.programacion_reporte_tipo))
    )
    if empleado_id:
        query = query.filter(Programacion.codigo_empleado_fk == empleado_id)
    total = query.with_entities(func.count(ProgramacionReporte.codigo_programacion_reporte_pk)).scalar()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return ProgramacionReporteListResponse(total=total, page=page, size=size, items=items)




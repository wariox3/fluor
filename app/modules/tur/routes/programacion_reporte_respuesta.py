from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.programacion_reporte_respuesta import ProgramacionReporteRespuesta
from app.modules.tur.schemas.programacion_reporte_respuesta import ProgramacionReporteRespuestaListResponse

router = APIRouter()


@router.get("/lista", response_model=ProgramacionReporteRespuestaListResponse)
def lista(programacion_reporte_id: Optional[int] = None, page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(ProgramacionReporteRespuesta)
    if programacion_reporte_id:
        query = query.filter(ProgramacionReporteRespuesta.codigo_programacion_reporte_fk == programacion_reporte_id)
    total = query.with_entities(func.count(ProgramacionReporteRespuesta.codigo_programacion_reporte_respuesta_pk)).scalar()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return ProgramacionReporteRespuestaListResponse(total=total, page=page, size=size, items=items)

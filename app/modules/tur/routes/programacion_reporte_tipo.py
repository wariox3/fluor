from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.programacion_reporte_tipo import ProgramacionReporteTipo
from app.modules.tur.schemas.programacion_reporte_tipo import ProgramacionReporteTipoListResponse

router = APIRouter()


@router.get("/lista", response_model=ProgramacionReporteTipoListResponse)
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(ProgramacionReporteTipo)
    total = query.with_entities(func.count(ProgramacionReporteTipo.codigo_programacion_reporte_tipo_pk)).scalar()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return ProgramacionReporteTipoListResponse(total=total, page=page, size=size, items=items)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.turno import Turno
from app.modules.tur.schemas.turno import TurnoListResponse, TurnoProgramacionRequest

router = APIRouter()


@router.get("/lista", response_model=TurnoListResponse)
def lista(page: int = 1, size: int = 50, turno_id: Optional[str] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Turno)
    if turno_id:
        query = query.filter(Turno.codigo_turno_pk == turno_id)
    total = query.with_entities(func.count(Turno.codigo_turno_pk)).scalar()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return TurnoListResponse(total=total, page=page, size=size, items=items)


@router.post("/programacion", response_model=TurnoListResponse)
def programacion(data: TurnoProgramacionRequest, page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Turno).filter(Turno.codigo_turno_pk.in_(data.turnos))
    total = query.with_entities(func.count(Turno.codigo_turno_pk)).scalar()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return TurnoListResponse(total=total, page=page, size=size, items=items)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.schemas.empleado import EmpleadoListResponse

router = APIRouter()


@router.get("/lista", response_model=EmpleadoListResponse)
def lista(page: int = 1, size: int = 50, numero_identificacion: Optional[str] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Empleado)
    if numero_identificacion:
        query = query.filter(Empleado.numero_identificacion.ilike(f"%{numero_identificacion}%"))
    total = query.with_entities(func.count(Empleado.codigo_empleado_pk)).scalar()
    offset = (page - 1) * size
    empleados = query.offset(offset).limit(size).all()
    return EmpleadoListResponse(total=total, page=page, size=size, items=empleados)
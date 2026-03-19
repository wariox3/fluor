from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import func
from io import BytesIO
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.models.reclamo import Reclamo
from app.modules.rhu.models.reclamo import Reclamo
from app.modules.rhu.schemas.reclamo import ReclamoListResponse

router = APIRouter()


@router.get("/lista", response_model=ReclamoListResponse)
def lista(page: int = 1, size: int = 50, empleado_id: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Reclamo)
    if empleado_id:
        query = query.filter(Reclamo.codigo_empleado_fk == empleado_id)
    total = query.with_entities(func.count(Reclamo.codigo_reclamo_pk)).scalar()
    offset = (page - 1) * size
    reclamos = query.offset(offset).limit(size).all()
    return ReclamoListResponse(total=total, page=page, size=size, items=reclamos)
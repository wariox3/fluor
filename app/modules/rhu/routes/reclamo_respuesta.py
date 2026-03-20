from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.reclamo_respuesta import ReclamoRespuesta
from app.modules.rhu.schemas.reclamo_respuesta import ReclamoRespuestaListResponse

router = APIRouter()


@router.get("/lista", response_model=ReclamoRespuestaListResponse)
def lista(reclamo_id: Optional[int] = None, page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(ReclamoRespuesta)
    if reclamo_id:
        query = query.filter(ReclamoRespuesta.codigo_reclamo_fk == reclamo_id)
    total = query.with_entities(func.count(ReclamoRespuesta.codigo_reclamo_respuesta_pk)).scalar()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return ReclamoRespuestaListResponse(total=total, page=page, size=size, items=items)

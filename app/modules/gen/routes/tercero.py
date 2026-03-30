from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.tercero import Tercero
from app.modules.gen.schemas.tercero import TerceroListResponse

router = APIRouter()

@router.get("/lista", response_model=TerceroListResponse)
def lista(page: int = 1, size: int = 50, numero_identificacion: Optional[str] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Tercero)
    if numero_identificacion:
        query = query.filter(Tercero.numero_identificacion.ilike(f"%{numero_identificacion}%"))
    total = query.with_entities(func.count(Tercero.codigo_tercero_pk)).scalar()
    offset = (page - 1) * size
    terceros = query.options(joinedload(Tercero.asesor)).offset(offset).limit(size).all()
    return TerceroListResponse(total=total, page=page, size=size, items=terceros)
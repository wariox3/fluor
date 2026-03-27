from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.core.config import DEFAULT_EMPRESA_ID
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.movimiento_tipo import MovimientoTipo
from app.modules.gen.schemas.movimiento_tipo import MovimientoTipoListResponse, MovimientoTipoResponse, MovimientoTipoCreate

router = APIRouter()

@router.get("/lista", response_model=MovimientoTipoListResponse)
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(MovimientoTipo)
    total = query.with_entities(func.count(MovimientoTipo.codigo_movimiento_tipo_pk)).scalar()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return MovimientoTipoListResponse(total=total, page=page, size=size, items=items)

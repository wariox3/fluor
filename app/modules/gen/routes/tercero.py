from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.tercero import Tercero
from app.modules.gen.schemas.tercero import TerceroListResponse

router = APIRouter()

@router.get("/lista", response_model=TerceroListResponse)
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    total = db.query(func.count(Tercero.codigo_tercero_pk)).scalar()
    offset = (page - 1) * size
    terceros = (
        db.query(Tercero)
        .options(joinedload(Tercero.ciudad))
        .offset(offset)
        .limit(size)
        .all()
    )
    return TerceroListResponse(total=total, page=page, size=size, items=terceros)
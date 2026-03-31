from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.enlace import Enlace
from app.modules.gen.schemas.enlace import EnlaceListResponse

router = APIRouter()


@router.get("/lista", response_model=EnlaceListResponse)
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    total = db.query(func.count(Enlace.codigo_enlace_pk)).scalar()
    offset = (page - 1) * size
    items = db.query(Enlace).order_by(Enlace.codigo_enlace_pk.desc()).offset(offset).limit(size).all()
    return EnlaceListResponse(total=total, page=page, size=size, items=items)

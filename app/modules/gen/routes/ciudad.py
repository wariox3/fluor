from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.modules.gen.models.ciudad import Ciudad
from app.modules.gen.schemas.ciudad import CiudadListResponse

router = APIRouter()

@router.get("/lista", response_model=CiudadListResponse)
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db)):
    total = db.query(func.count(Ciudad.codigo_ciudad_pk)).scalar()
    offset = (page - 1) * size
    ciudades = (
        db.query(Ciudad)
        .offset(offset)
        .limit(size)
        .all()
    )
    return CiudadListResponse(total=total, page=page, size=size, items=ciudades)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.ciudad import Ciudad
from app.modules.gen.schemas.ciudad import CiudadListResponse

router = APIRouter()

@router.get("/lista", response_model=CiudadListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    nombre: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Ciudad)
    if nombre:
        query = query.filter(Ciudad.nombre.ilike(f"%{nombre}%"))
    total = query.with_entities(func.count(Ciudad.codigo_ciudad_pk)).scalar()
    offset = (page - 1) * size
    ciudades = query.offset(offset).limit(size).all()
    return CiudadListResponse(total=total, page=page, size=size, items=ciudades)
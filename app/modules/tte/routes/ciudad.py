from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.departamento import Departamento
from app.modules.tte.schemas.ciudad import CiudadListResponse, CiudadDescargarResponse, CiudadSincronizarResponse

router = APIRouter()


@router.get("/buscar", response_model=CiudadListResponse)
def buscar(
    page: int = 1,
    size: int = 50,
    pk: Optional[str] = None,
    nombre: Optional[str] = None,
    codigo_interface: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Ciudad)
    if pk is not None:
        query = query.filter(Ciudad.codigo_ciudad_pk == pk)
    if nombre is not None:
        query = query.filter(Ciudad.nombre.ilike(f"%{nombre}%"))
    if codigo_interface is not None:
        query = query.filter(Ciudad.codigo_interface == codigo_interface)
    total = query.with_entities(func.count(Ciudad.codigo_ciudad_pk)).scalar()
    offset = (page - 1) * size
    ciudades = (
        query.options(joinedload(Ciudad.ruta), joinedload(Ciudad.departamento))
        .order_by(Ciudad.nombre.asc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return CiudadListResponse(total=total, page=page, size=size, items=ciudades)


@router.get(
    "/descargar",
    response_model=list[CiudadDescargarResponse],
    description="Catálogo completo sin paginar (JSON, no archivo) para que la aplicación lo guarde en caché.",
)
def descargar(db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    return (
        db.query(Ciudad.codigo_ciudad_pk, Ciudad.nombre, Departamento.nombre.label("departamento_nombre"))
        .outerjoin(Departamento, Ciudad.codigo_departamento_fk == Departamento.codigo_departamento_pk)
        .order_by(Ciudad.codigo_ciudad_pk.asc())
        .all()
    )


@router.get(
    "/lista-sincronizar",
    response_model=list[CiudadSincronizarResponse],
    deprecated=True,
    description="Obsoleta: usar /descargar.",
)
def lista_sincronizar(db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    return db.query(Ciudad).order_by(Ciudad.codigo_ciudad_pk.asc()).all()

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.core.rate_limit import limiter
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.novedad_tipo import NovedadTipo
from app.modules.tte.schemas.novedad_tipo import NovedadTipoListResponse, NovedadTipoResponse

router = APIRouter()


@router.get("/lista", response_model=NovedadTipoListResponse)
@limiter.limit("10/minute")
def lista(
    request: Request,
    response: Response,
    page: int = 1,
    size: int = 50,
    pk: Optional[str] = None,
    nombre: Optional[str] = None,
    interna: Optional[bool] = None,
    aplica_movil: Optional[bool] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(NovedadTipo)
    if pk:
        query = query.filter(NovedadTipo.codigo_novedad_tipo_pk == pk)
    if nombre:
        query = query.filter(NovedadTipo.nombre.ilike(f"%{nombre}%"))
    if interna is not None:
        query = query.filter(NovedadTipo.interna == interna)
    if aplica_movil is not None:
        query = query.filter(NovedadTipo.aplica_movil == aplica_movil)

    total = query.with_entities(func.count(NovedadTipo.codigo_novedad_tipo_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(NovedadTipo.nombre.asc()).offset(offset).limit(size).all()
    return NovedadTipoListResponse(total=total, page=page, size=size, items=items)


@router.get(
    "/lista-movil",
    response_model=list[NovedadTipoResponse],
    description="Tipos de novedad que aplican para la aplicación móvil, sin paginar.",
)
def lista_movil(db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    return (
        db.query(NovedadTipo)
        .filter(NovedadTipo.aplica_movil.is_(True))
        .order_by(NovedadTipo.nombre.asc())
        .all()
    )

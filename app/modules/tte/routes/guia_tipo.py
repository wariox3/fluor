from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.guia_tipo import GuiaTipo
from app.modules.tte.schemas.guia_tipo import GuiaTipoDescargarResponse, GuiaTipoListResponse

router = APIRouter()


@router.get("/buscar", response_model=GuiaTipoListResponse)
def buscar(
    page: int = 1,
    size: int = 50,
    pk: Optional[str] = None,
    nombre: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(GuiaTipo)

    if pk:
        query = query.filter(GuiaTipo.codigo_guia_tipo_pk == pk)
    if nombre:
        query = query.filter(GuiaTipo.nombre.ilike(f"%{nombre}%"))

    total = query.with_entities(func.count(GuiaTipo.codigo_guia_tipo_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(GuiaTipo.nombre.asc()).offset(offset).limit(size).all()

    return GuiaTipoListResponse(total=total, page=page, size=size, items=items)


@router.get(
    "/descargar",
    response_model=list[GuiaTipoDescargarResponse],
    description="Catálogo completo sin paginar (JSON, no archivo) para que la aplicación lo guarde en caché.",
)
def descargar(db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    return (
        db.query(
            GuiaTipo.codigo_guia_tipo_pk,
            GuiaTipo.nombre,
            GuiaTipo.codigo_pago_fk,
            GuiaTipo.codigo_forma_pago,
            GuiaTipo.validar_flete,
            GuiaTipo.genera_cobro,
        )
        .order_by(GuiaTipo.codigo_guia_tipo_pk.asc())
        .all()
    )

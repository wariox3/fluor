from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.seg.models.usuario_configuracion import UsuarioConfiguracion
from app.modules.seg.schemas.usuario_configuracion import UsuarioConfiguracionListResponse, UsuarioConfiguracionResponse

router = APIRouter()


@router.get("/lista", response_model=UsuarioConfiguracionListResponse)
def lista(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    username_pk: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(UsuarioConfiguracion)
    if username_pk:
        query = query.filter(UsuarioConfiguracion.username_pk.ilike(f"%{username_pk}%"))
    total = query.with_entities(func.count(UsuarioConfiguracion.username_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(UsuarioConfiguracion.username_pk.asc()).offset(offset).limit(size).all()
    return UsuarioConfiguracionListResponse(total=total, page=page, size=size, items=items)


@router.get("/detalle/{username_pk}", response_model=UsuarioConfiguracionResponse)
def detalle(username_pk: str, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    usuario_configuracion = db.query(UsuarioConfiguracion).filter(UsuarioConfiguracion.username_pk == username_pk).first()

    if not usuario_configuracion:
        raise HTTPException(status_code=404, detail="Configuración de usuario no encontrada")

    return usuario_configuracion

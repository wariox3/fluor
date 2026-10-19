from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.identificacion import Identificacion
from app.modules.gen.schemas.identificacion import IdentificacionListResponse, IdentificacionResponse

router = APIRouter()


@router.get("/lista", response_model=IdentificacionListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    total = db.query(func.count(Identificacion.codigo_identificacion_pk)).scalar()
    offset = (page - 1) * size
    identificaciones = (
        db.query(Identificacion)
        .order_by(Identificacion.codigo_identificacion_pk)
        .offset(offset)
        .limit(size)
        .all()
    )
    return IdentificacionListResponse(total=total, page=page, size=size, items=identificaciones)


@router.get(
    "/descargar",
    response_model=list[IdentificacionResponse],
    description="Catálogo completo sin paginar (JSON, no archivo) para que la aplicación lo guarde en caché.",
)
def descargar(
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    return db.query(Identificacion).order_by(Identificacion.codigo_identificacion_pk).all()


@router.get("/{codigo}", response_model=IdentificacionResponse)
def detalle(
    codigo: str,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    identificacion = db.query(Identificacion).filter(Identificacion.codigo_identificacion_pk == codigo).first()
    if not identificacion:
        raise HTTPException(status_code=404, detail="Identificación no encontrada")
    return identificacion

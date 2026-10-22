from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.asesor import Asesor
from app.modules.gen.schemas.asesor import AsesorDescargarResponse, AsesorListResponse, AsesorResponse

router = APIRouter()


@router.get("/lista", response_model=AsesorListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    total = db.query(func.count(Asesor.codigo_asesor_pk)).scalar()
    offset = (page - 1) * size
    asesores = db.query(Asesor).offset(offset).limit(size).all()
    return AsesorListResponse(total=total, page=page, size=size, items=asesores)


@router.get(
    "/descargar",
    response_model=list[AsesorDescargarResponse],
    description="Asesores activos sin paginar (JSON, no archivo) para que la aplicación los guarde en caché.",
)
def descargar(db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    return (
        db.query(Asesor.codigo_asesor_pk, Asesor.nombre)
        .filter(Asesor.estado_inactivo.is_(False))
        .order_by(Asesor.nombre.asc())
        .all()
    )

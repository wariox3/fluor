from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.regimen import Regimen
from app.modules.gen.schemas.regimen import RegimenDescargarResponse

router = APIRouter()


@router.get(
    "/descargar",
    response_model=list[RegimenDescargarResponse],
    description="Catálogo completo sin paginar (JSON, no archivo) para que la aplicación lo guarde en caché.",
)
def descargar(db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    return (
        db.query(Regimen.codigo_regimen_pk, Regimen.nombre)
        .order_by(Regimen.nombre.asc())
        .all()
    )

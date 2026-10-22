from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.tipo_persona import TipoPersona
from app.modules.gen.schemas.tipo_persona import TipoPersonaDescargarResponse

router = APIRouter()


@router.get(
    "/descargar",
    response_model=list[TipoPersonaDescargarResponse],
    description="Catálogo completo sin paginar (JSON, no archivo) para que la aplicación lo guarde en caché.",
)
def descargar(db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    return (
        db.query(TipoPersona.codigo_tipo_persona_pk, TipoPersona.nombre)
        .order_by(TipoPersona.nombre.asc())
        .all()
    )

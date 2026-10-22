from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.gen.models.configuracion import Configuracion
from app.modules.gen.schemas.configuracion import ConfiguracionGuiaNuevoResponse

router = APIRouter()


@router.get(
    "/guia-nuevo",
    response_model=ConfiguracionGuiaNuevoResponse,
    description="Valores generales que usa la creación de guías. Siempre lee la configuración 1.",
)
def guia_nuevo(db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    configuracion = (
        db.query(
            Configuracion.codigo_precio_general_fk,
            Configuracion.codigo_condicion_general_fk,
            Configuracion.codigo_asesor_general_fk,
        )
        .filter(Configuracion.codigo_configuracion_pk == 1)
        .first()
    )

    if not configuracion:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")

    return configuracion

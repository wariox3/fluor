from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.guia import Guia
from app.modules.tte.models.operacion import Operacion
from app.modules.tte.models.seguimiento import Seguimiento
from app.modules.tte.models.seguimiento_tipo import SeguimientoTipo
from app.modules.tte.schemas.seguimiento import SeguimientoCreateRequest, SeguimientoResponse

router = APIRouter()


@router.post("/nuevo", response_model=SeguimientoResponse)
def nuevo(payload: SeguimientoCreateRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    if not db.query(Guia).filter(Guia.codigo_guia_pk == payload.codigo_guia_fk).first():
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    if payload.codigo_seguimiento_tipo_fk is not None:
        if not db.query(SeguimientoTipo).filter(SeguimientoTipo.codigo_seguimiento_tipo_pk == payload.codigo_seguimiento_tipo_fk).first():
            raise HTTPException(status_code=404, detail="Tipo de seguimiento no encontrado")

    if payload.codigo_operacion_fk is not None:
        if not db.query(Operacion).filter(Operacion.codigo_operacion_pk == payload.codigo_operacion_fk).first():
            raise HTTPException(status_code=404, detail="Operación no encontrada")

    seguimiento = Seguimiento(
        codigo_guia_fk=payload.codigo_guia_fk,
        codigo_seguimiento_tipo_fk=payload.codigo_seguimiento_tipo_fk,
        codigo_operacion_fk=payload.codigo_operacion_fk,
        fecha=datetime.now(),
        fecha_seguimiento=payload.fecha_seguimiento or datetime.now(),
        usuario=current_user["sub"],
        comentario=payload.comentario,
        datos=payload.datos,
        latitud=payload.latitud,
        longitud=payload.longitud,
    )

    db.add(seguimiento)
    db.commit()
    db.refresh(seguimiento)

    return seguimiento

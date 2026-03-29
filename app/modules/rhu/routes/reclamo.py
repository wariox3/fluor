from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from io import BytesIO
from app.core.config import DEFAULT_EMPRESA_ID
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.models.reclamo import Reclamo
from app.modules.rhu.models.reclamo_concepto import ReclamoConcepto
from app.modules.rhu.schemas.reclamo import ReclamoListResponse, ReclamoCreate, ReclamoResponse
from datetime import date

router = APIRouter()


@router.post("/nuevo", response_model=ReclamoResponse)
def nuevo(data: ReclamoCreate, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    empleado = db.query(Empleado).filter(Empleado.codigo_empleado_pk == data.codigo_empleado_fk).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    concepto = db.query(ReclamoConcepto).filter(ReclamoConcepto.codigo_reclamo_concepto_pk == data.codigo_reclamo_concepto_fk).first()
    if not concepto:
        raise HTTPException(status_code=404, detail="Concepto de reclamo no encontrado")

    reclamo = Reclamo(
        codigo_empleado_fk=data.codigo_empleado_fk,
        codigo_reclamo_concepto_fk=data.codigo_reclamo_concepto_fk,
        fecha=date.today(),
        descripcion=data.descripcion,
        estado_autorizado=False,
        estado_aprobado=False,
        estado_anulado=False,
        estado_cerrado=False,
        estado_atendido=False,
        cantidad_respuestas=0,
        usuario="empleado.co",
        codigo_empresa_fk=DEFAULT_EMPRESA_ID,
    )
    db.add(reclamo)
    db.commit()
    db.refresh(reclamo)
    return reclamo


@router.get("/lista", response_model=ReclamoListResponse)
def lista(page: int = 1, size: int = 50, empleado_id: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Reclamo).options(joinedload(Reclamo.reclamo_concepto))
    if empleado_id:
        query = query.filter(Reclamo.codigo_empleado_fk == empleado_id)
    total = query.with_entities(func.count(Reclamo.codigo_reclamo_pk)).scalar()
    offset = (page - 1) * size
    reclamos = query.offset(offset).limit(size).all()
    return ReclamoListResponse(total=total, page=page, size=size, items=reclamos)
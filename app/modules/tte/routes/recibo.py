from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.guia import Guia
from app.modules.tte.models.operacion import Operacion
from app.modules.tte.models.recibo import Recibo
from app.modules.tte.schemas.recibo import ReciboCreateRequest, ReciboListResponse, ReciboResponse

router = APIRouter()


@router.post("/nuevo", response_model=ReciboResponse)
def nuevo(payload: ReciboCreateRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    fks = [
        (Guia, Guia.codigo_guia_pk, payload.codigo_guia_fk, "Guía no encontrada"),
        (Operacion, Operacion.codigo_operacion_pk, payload.codigo_operacion_fk, "Operación no encontrada"),
        (Tercero, Tercero.codigo_tercero_pk, payload.codigo_tercero_fk, "Tercero no encontrado"),
    ]
    for modelo, columna, valor, mensaje in fks:
        if valor is not None and not db.query(modelo).filter(columna == valor).first():
            raise HTTPException(status_code=404, detail=mensaje)

    recibo = Recibo(
        codigo_recibo_tipo_fk=payload.codigo_recibo_tipo_fk,
        codigo_guia_fk=payload.codigo_guia_fk,
        codigo_operacion_fk=payload.codigo_operacion_fk,
        codigo_tercero_fk=payload.codigo_tercero_fk,
        codigo_cliente_fk=payload.codigo_cliente_fk,
        numero=payload.numero or 0.0,
        fecha=payload.fecha or date.today(),
        vr_flete=payload.vr_flete,
        vr_manejo=payload.vr_manejo,
        vr_total=payload.vr_flete + payload.vr_manejo,
        estado_relacion=False,
    )

    db.add(recibo)
    db.commit()
    db.refresh(recibo)

    return recibo


@router.get("/lista", response_model=ReciboListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    codigo_guia_fk: Optional[int] = None,
    codigo_tercero_fk: Optional[int] = None,
    codigo_operacion_fk: Optional[str] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    estado_relacion: Optional[bool] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Recibo)
    if codigo_guia_fk is not None:
        query = query.filter(Recibo.codigo_guia_fk == codigo_guia_fk)
    if codigo_tercero_fk is not None:
        query = query.filter(Recibo.codigo_tercero_fk == codigo_tercero_fk)
    if codigo_operacion_fk is not None:
        query = query.filter(Recibo.codigo_operacion_fk == codigo_operacion_fk)
    if fecha_desde is not None:
        query = query.filter(Recibo.fecha >= fecha_desde)
    if fecha_hasta is not None:
        query = query.filter(Recibo.fecha <= fecha_hasta)
    if estado_relacion is not None:
        query = query.filter(Recibo.estado_relacion == estado_relacion)

    total = query.with_entities(func.count(Recibo.codigo_recibo_pk)).scalar()
    offset = (page - 1) * size
    items = (
        query.options(joinedload(Recibo.tercero), joinedload(Recibo.operacion))
        .order_by(Recibo.codigo_recibo_pk.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    return ReciboListResponse(total=total, page=page, size=size, items=items)


@router.get("/detalle/{codigo_recibo_pk}", response_model=ReciboResponse)
def detalle(codigo_recibo_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    recibo = (
        db.query(Recibo)
        .options(joinedload(Recibo.tercero), joinedload(Recibo.operacion))
        .filter(Recibo.codigo_recibo_pk == codigo_recibo_pk)
        .first()
    )

    if not recibo:
        raise HTTPException(status_code=404, detail="Recibo no encontrado")

    return recibo

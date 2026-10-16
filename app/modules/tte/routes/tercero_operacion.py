from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.tercero_operacion import TerceroOperacion
from app.modules.tte.schemas.tercero_operacion import (
    TerceroOperacionCreateRequest,
    TerceroOperacionResponse,
    TerceroOperacionListResponse,
)

router = APIRouter()


@router.post("/nuevo", response_model=TerceroOperacionResponse)
def nuevo(payload: TerceroOperacionCreateRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    if not db.query(Tercero).filter(Tercero.codigo_tercero_pk == payload.codigo_tercero_fk).first():
        raise HTTPException(status_code=404, detail="Tercero no encontrado")

    tercero_operacion = TerceroOperacion(
        codigo_tercero_fk=payload.codigo_tercero_fk,
        codigo=payload.codigo,
        nombre=payload.nombre,
    )

    db.add(tercero_operacion)
    db.commit()
    db.refresh(tercero_operacion)

    return tercero_operacion


@router.get("/lista", response_model=TerceroOperacionListResponse)
def lista(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    codigo_tercero_fk: Optional[int] = None,
    codigo: Optional[str] = None,
    nombre: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(TerceroOperacion)
    if codigo_tercero_fk is not None:
        query = query.filter(TerceroOperacion.codigo_tercero_fk == codigo_tercero_fk)
    if codigo is not None:
        query = query.filter(TerceroOperacion.codigo == codigo)
    if nombre is not None:
        query = query.filter(TerceroOperacion.nombre.ilike(f"%{nombre}%"))
    total = query.with_entities(func.count(TerceroOperacion.codigo_tercero_operacion_pk)).scalar()
    offset = (page - 1) * size
    items = (
        query.options(joinedload(TerceroOperacion.tercero))
        .order_by(TerceroOperacion.codigo_tercero_operacion_pk.asc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return TerceroOperacionListResponse(total=total, page=page, size=size, items=items)


@router.get("/detalle/{codigo_tercero_operacion_pk}", response_model=TerceroOperacionResponse)
def detalle(codigo_tercero_operacion_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    tercero_operacion = (
        db.query(TerceroOperacion)
        .options(joinedload(TerceroOperacion.tercero))
        .filter(TerceroOperacion.codigo_tercero_operacion_pk == codigo_tercero_operacion_pk)
        .first()
    )

    if not tercero_operacion:
        raise HTTPException(status_code=404, detail="Tercero operación no encontrado")

    return tercero_operacion

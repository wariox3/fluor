from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.tte.models.condicion import Condicion
from app.modules.tte.schemas.condicion import (
    CondicionBuscarListResponse,
    CondicionDetalleResponse,
    CondicionListResponse,
)

router = APIRouter()


@router.get("/lista", response_model=CondicionListResponse)
def lista(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    codigo_condicion_pk: Optional[int] = None,
    nombre: Optional[str] = None,
    codigo_precio_fk: Optional[int] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Condicion)
    if codigo_condicion_pk is not None:
        query = query.filter(Condicion.codigo_condicion_pk == codigo_condicion_pk)
    if nombre:
        query = query.filter(Condicion.nombre.ilike(f"%{nombre}%"))
    if codigo_precio_fk is not None:
        query = query.filter(Condicion.codigo_precio_fk == codigo_precio_fk)
    total = query.with_entities(func.count(Condicion.codigo_condicion_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(Condicion.codigo_condicion_pk.asc()).offset(offset).limit(size).all()
    return CondicionListResponse(total=total, page=page, size=size, items=items)


@router.get("/buscar", response_model=CondicionBuscarListResponse)
def buscar(
    page: int = Query(1, ge=1),
    codigo_condicion_pk: Optional[int] = None,
    nombre: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Condicion)
    if codigo_condicion_pk is not None:
        query = query.filter(Condicion.codigo_condicion_pk == codigo_condicion_pk)
    if nombre:
        query = query.filter(Condicion.nombre.ilike(f"%{nombre}%"))
    total = query.with_entities(func.count(Condicion.codigo_condicion_pk)).scalar()
    size = 10
    offset = (page - 1) * size
    items = (
        query.with_entities(Condicion.codigo_condicion_pk, Condicion.nombre)
        .order_by(Condicion.nombre.asc(), Condicion.codigo_condicion_pk.asc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return CondicionBuscarListResponse(total=total, page=page, size=size, items=items)


@router.get("/detalle/{codigo_condicion_pk}", response_model=CondicionDetalleResponse)
def detalle(codigo_condicion_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    condicion = db.query(Condicion).filter(Condicion.codigo_condicion_pk == codigo_condicion_pk).first()

    if not condicion:
        raise HTTPException(status_code=404, detail="Condición no encontrada")

    return condicion

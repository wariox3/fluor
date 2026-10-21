from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.config import DEFAULT_EMPRESA_ID
from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.gen.models.identificacion import Identificacion
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.destinatario import Destinatario
from app.modules.tte.schemas.destinatario import (
    DestinatarioCreateRequest,
    DestinatarioListResponse,
    DestinatarioResponse,
)

router = APIRouter()


@router.post("/nuevo", response_model=DestinatarioResponse)
def nuevo(payload: DestinatarioCreateRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    if not db.query(Identificacion).filter(Identificacion.codigo_identificacion_pk == payload.codigo_identificacion_fk).first():
        raise HTTPException(status_code=404, detail="Identificación no encontrada")
    if payload.codigo_ciudad_fk and not db.query(Ciudad).filter(Ciudad.codigo_ciudad_pk == payload.codigo_ciudad_fk).first():
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")
    if payload.codigo_tercero_fk and not db.query(Tercero).filter(Tercero.codigo_tercero_pk == payload.codigo_tercero_fk).first():
        raise HTTPException(status_code=404, detail="Tercero no encontrado")
    existe = (
        db.query(Destinatario.codigo_destinatario_pk)
        .filter(
            Destinatario.codigo_empresa_fk == DEFAULT_EMPRESA_ID,
            Destinatario.codigo_identificacion_fk == payload.codigo_identificacion_fk,
            Destinatario.numero_identificacion == payload.numero_identificacion,
        )
        .first()
    )
    if existe:
        raise HTTPException(status_code=409, detail="Ya existe un destinatario con ese tipo y número de identificación")

    datos = payload.model_dump()
    # Si no llega nombre corto, se arma con nombres y apellidos
    if not datos["nombre_corto"]:
        partes = [datos["nombre1"], datos["nombre2"], datos["apellido1"], datos["apellido2"]]
        datos["nombre_corto"] = " ".join(p.strip() for p in partes if p and p.strip()) or None

    destinatario = Destinatario(**datos, codigo_empresa_fk=DEFAULT_EMPRESA_ID)

    db.add(destinatario)
    db.commit()
    db.refresh(destinatario)

    return destinatario


@router.get("/lista", response_model=DestinatarioListResponse)
def lista(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    codigo_destinatario_pk: Optional[int] = None,
    codigo_identificacion_fk: Optional[str] = None,
    numero_identificacion: Optional[str] = None,
    nombre_corto: Optional[str] = None,
    codigo_ciudad_fk: Optional[str] = None,
    codigo_tercero_fk: Optional[int] = None,
    estado_inactivo: Optional[bool] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Destinatario)
    if codigo_destinatario_pk is not None:
        query = query.filter(Destinatario.codigo_destinatario_pk == codigo_destinatario_pk)
    if codigo_identificacion_fk is not None:
        query = query.filter(Destinatario.codigo_identificacion_fk == codigo_identificacion_fk)
    if numero_identificacion is not None:
        query = query.filter(Destinatario.numero_identificacion == numero_identificacion)
    if nombre_corto is not None:
        query = query.filter(Destinatario.nombre_corto.ilike(f"%{nombre_corto}%"))
    if codigo_ciudad_fk is not None:
        query = query.filter(Destinatario.codigo_ciudad_fk == codigo_ciudad_fk)
    if codigo_tercero_fk is not None:
        query = query.filter(Destinatario.codigo_tercero_fk == codigo_tercero_fk)
    if estado_inactivo is not None:
        query = query.filter(Destinatario.estado_inactivo == estado_inactivo)
    total = query.with_entities(func.count(Destinatario.codigo_destinatario_pk)).scalar()
    offset = (page - 1) * size
    items = (
        query.options(
            joinedload(Destinatario.identificacion),
            joinedload(Destinatario.ciudad),
            joinedload(Destinatario.tercero),
        )
        .order_by(Destinatario.codigo_destinatario_pk.asc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return DestinatarioListResponse(total=total, page=page, size=size, items=items)

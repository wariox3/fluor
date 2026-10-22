from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.core.config import DEFAULT_EMPRESA_ID
from app.modules.gen.models.asesor import Asesor
from app.modules.gen.models.ciudad import Ciudad
from app.modules.gen.models.identificacion import Identificacion
from app.modules.gen.models.regimen import Regimen
from app.modules.gen.models.tipo_persona import TipoPersona
from app.modules.gen.models.tercero import Tercero
from app.modules.gen.schemas.tercero import TerceroBuscarListResponse, TerceroCreateRequest, TerceroDetalleResponse, TerceroListResponse
from app.modules.tte.models.condicion import Condicion
from app.modules.tte.models.operacion import Operacion

router = APIRouter()

@router.post("/nuevo", response_model=TerceroDetalleResponse)
def nuevo(payload: TerceroCreateRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    fks = [
        (Identificacion, Identificacion.codigo_identificacion_pk, payload.codigo_identificacion_fk, "Tipo de identificación no encontrado"),
        (Ciudad, Ciudad.codigo_ciudad_pk, payload.codigo_ciudad_fk, "Ciudad no encontrada"),
        (TipoPersona, TipoPersona.codigo_tipo_persona_pk, payload.codigo_tipo_persona_fk, "Tipo de persona no encontrado"),
        (Regimen, Regimen.codigo_regimen_pk, payload.codigo_regimen_fk, "Régimen no encontrado"),
        (Asesor, Asesor.codigo_asesor_pk, payload.codigo_asesor_fk, "Asesor no encontrado"),
        (Condicion, Condicion.codigo_condicion_pk, payload.codigo_condicion_fk, "Condición no encontrada"),
        (Operacion, Operacion.codigo_operacion_pk, payload.codigo_operacion_fk, "Operación no encontrada"),
    ]
    for modelo, columna, valor, mensaje in fks:
        if valor is not None and not db.query(modelo).filter(columna == valor).first():
            raise HTTPException(status_code=404, detail=mensaje)

    existe = db.query(Tercero.codigo_tercero_pk).filter(
        Tercero.numero_identificacion == payload.numero_identificacion,
    ).first()
    if existe:
        raise HTTPException(status_code=409, detail=f"Ya existe un tercero con el número de identificación {payload.numero_identificacion}")

    # Si no llega nombre_corto se arma con los nombres y apellidos (persona natural)
    nombre_corto = payload.nombre_corto or " ".join(
        p for p in (payload.nombre1, payload.nombre2, payload.apellido1, payload.apellido2) if p
    )
    if not nombre_corto.strip():
        raise HTTPException(status_code=422, detail="Debe enviar nombre_corto o nombres y apellidos")

    datos = payload.model_dump(exclude={"nombre_corto"})
    tercero = Tercero(
        **datos,
        nombre_corto=nombre_corto.strip(),
        codigo_empresa_fk=DEFAULT_EMPRESA_ID,
        estado_inactivo=False,
        usuario=current_user["sub"],
    )

    db.add(tercero)
    db.commit()
    db.refresh(tercero)

    return tercero


@router.get("/lista", response_model=TerceroListResponse)
def lista(page: int = 1, size: int = 50, numero_identificacion: Optional[str] = None, nombre_corto: Optional[str] = None, codigo_tercero_pk: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Tercero)
    if numero_identificacion:
        query = query.filter(Tercero.numero_identificacion.ilike(f"%{numero_identificacion}%"))
    if nombre_corto:
        query = query.filter(Tercero.nombre_corto.ilike(f"%{nombre_corto}%"))
    if codigo_tercero_pk is not None:
        query = query.filter(Tercero.codigo_tercero_pk == codigo_tercero_pk)        
    total = query.with_entities(func.count(Tercero.codigo_tercero_pk)).scalar()
    offset = (page - 1) * size
    terceros = (
        query.options(joinedload(Tercero.asesor), joinedload(Tercero.condicion))
        .order_by(Tercero.nombre_corto.asc(), Tercero.codigo_tercero_pk.asc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return TerceroListResponse(total=total, page=page, size=size, items=terceros)


@router.get("/buscar", response_model=TerceroBuscarListResponse)
def buscar(
    page: int = Query(1, ge=1),
    numero_identificacion: Optional[str] = None,
    nombre_corto: Optional[str] = None,
    codigo_tercero_pk: Optional[int] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Tercero)
    if numero_identificacion:
        query = query.filter(Tercero.numero_identificacion.ilike(f"%{numero_identificacion}%"))
    if nombre_corto:
        query = query.filter(Tercero.nombre_corto.ilike(f"%{nombre_corto}%"))
    if codigo_tercero_pk is not None:
        query = query.filter(Tercero.codigo_tercero_pk == codigo_tercero_pk)
    total = query.with_entities(func.count(Tercero.codigo_tercero_pk)).scalar()
    size = 10
    offset = (page - 1) * size
    items = (
        query.outerjoin(Condicion, Tercero.codigo_condicion_fk == Condicion.codigo_condicion_pk)
        .with_entities(
            Tercero.codigo_tercero_pk,
            Tercero.numero_identificacion,
            Tercero.nombre_corto,
            Condicion.nombre.label("condicion_nombre"),
            Tercero.estado_inactivo,
        )
        .order_by(Tercero.nombre_corto.asc(), Tercero.codigo_tercero_pk.asc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return TerceroBuscarListResponse(total=total, page=page, size=size, items=items)


@router.get("/detalle/{codigo_tercero_pk}", response_model=TerceroDetalleResponse)
def detalle(codigo_tercero_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    tercero = (
        db.query(Tercero)
        .options(
            joinedload(Tercero.ciudad),
            joinedload(Tercero.asesor),
            joinedload(Tercero.condicion),
            joinedload(Tercero.tipo_persona),
            joinedload(Tercero.regimen),
        )
        .filter(Tercero.codigo_tercero_pk == codigo_tercero_pk)
        .first()
    )

    if not tercero:
        raise HTTPException(status_code=404, detail="Tercero no encontrado")

    return tercero

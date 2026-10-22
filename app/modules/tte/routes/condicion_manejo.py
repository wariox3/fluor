from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.condicion_manejo import CondicionManejo
from app.modules.tte.models.zona import Zona
from app.modules.tte.schemas.condicion_manejo import CondicionManejoListResponse, CondicionManejoLiquidarRequest, CondicionManejoLiquidarResponse, CondicionManejoResponse
from app.modules.tte.services import guia as guia_service

router = APIRouter()


def _con_nombres(query):
    """Agrega los nombres de tercero, ciudades y zona (LEFT JOIN) y deja solo las columnas de la respuesta."""
    ciudad_origen = aliased(Ciudad)
    ciudad_destino = aliased(Ciudad)
    return (
        query.outerjoin(Tercero, CondicionManejo.codigo_tercero_fk == Tercero.codigo_tercero_pk)
        .outerjoin(ciudad_origen, CondicionManejo.codigo_ciudad_origen_fk == ciudad_origen.codigo_ciudad_pk)
        .outerjoin(ciudad_destino, CondicionManejo.codigo_ciudad_destino_fk == ciudad_destino.codigo_ciudad_pk)
        .outerjoin(Zona, CondicionManejo.codigo_zona_fk == Zona.codigo_zona_pk)
        .with_entities(
            CondicionManejo.codigo_condicion_manejo_pk,
            CondicionManejo.codigo_cliente_fk,
            CondicionManejo.codigo_tercero_fk,
            Tercero.nombre_corto.label("tercero_nombre"),
            CondicionManejo.codigo_ciudad_origen_fk,
            ciudad_origen.nombre.label("ciudad_origen_nombre"),
            CondicionManejo.codigo_ciudad_destino_fk,
            ciudad_destino.nombre.label("ciudad_destino_nombre"),
            CondicionManejo.codigo_zona_fk,
            Zona.nombre.label("zona_nombre"),
            CondicionManejo.codigo_cobertura_fk,
            CondicionManejo.codigo_pago_fk,
            CondicionManejo.porcentaje,
            CondicionManejo.minimo_unidad,
            CondicionManejo.minimo_despacho,
        )
    )


@router.get("/lista", response_model=CondicionManejoListResponse)
def lista(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    codigo_tercero_fk: Optional[int] = None,
    codigo_ciudad_origen_fk: Optional[str] = None,
    codigo_ciudad_destino_fk: Optional[str] = None,
    codigo_zona_fk: Optional[str] = None,
    codigo_pago_fk: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(CondicionManejo)
    if codigo_tercero_fk is not None:
        query = query.filter(CondicionManejo.codigo_tercero_fk == codigo_tercero_fk)
    if codigo_ciudad_origen_fk is not None:
        query = query.filter(CondicionManejo.codigo_ciudad_origen_fk == codigo_ciudad_origen_fk)
    if codigo_ciudad_destino_fk is not None:
        query = query.filter(CondicionManejo.codigo_ciudad_destino_fk == codigo_ciudad_destino_fk)
    if codigo_zona_fk is not None:
        query = query.filter(CondicionManejo.codigo_zona_fk == codigo_zona_fk)
    if codigo_pago_fk is not None:
        query = query.filter(CondicionManejo.codigo_pago_fk == codigo_pago_fk)
    total = query.with_entities(func.count(CondicionManejo.codigo_condicion_manejo_pk)).scalar()

    offset = (page - 1) * size
    items = (
        _con_nombres(query)
        .order_by(CondicionManejo.codigo_condicion_manejo_pk.asc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return CondicionManejoListResponse(total=total, page=page, size=size, items=items)


@router.post(
    "/liquidar",
    response_model=CondicionManejoLiquidarResponse,
    description="Busca la condición del tercero que aplica para liquidar (replica apiWindowsLiquidar de PHP).",
)
def liquidar(payload: CondicionManejoLiquidarRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    resultado = guia_service.buscar_condicion_manejo(
        db,
        tercero=payload.codigo_tercero_fk,
        origen=payload.codigo_ciudad_origen_fk,
        destino=payload.codigo_ciudad_destino_fk,
        zona=payload.codigo_zona_fk,
        cobertura=payload.codigo_cobertura_fk,
        pago=payload.codigo_pago_fk,
    )
    if not resultado:
        raise HTTPException(status_code=404, detail="No se encontraron resultados")
    return resultado


@router.get("/detalle/{codigo_condicion_manejo_pk}", response_model=CondicionManejoResponse)
def detalle(codigo_condicion_manejo_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    condicion_manejo = _con_nombres(db.query(CondicionManejo).filter(CondicionManejo.codigo_condicion_manejo_pk == codigo_condicion_manejo_pk)).first()

    if not condicion_manejo:
        raise HTTPException(status_code=404, detail="Condición manejo no encontrada")

    return condicion_manejo

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.condicion_flete import CondicionFlete
from app.modules.tte.models.zona import Zona
from app.modules.tte.schemas.condicion_flete import CondicionFleteListResponse, CondicionFleteLiquidarRequest, CondicionFleteLiquidarResponse, CondicionFleteResponse
from app.modules.tte.services import guia as guia_service

router = APIRouter()


def _con_nombres(query):
    """Agrega los nombres de tercero, ciudades y zona (LEFT JOIN) y deja solo las columnas de la respuesta."""
    ciudad_origen = aliased(Ciudad)
    ciudad_destino = aliased(Ciudad)
    return (
        query.outerjoin(Tercero, CondicionFlete.codigo_tercero_fk == Tercero.codigo_tercero_pk)
        .outerjoin(ciudad_origen, CondicionFlete.codigo_ciudad_origen_fk == ciudad_origen.codigo_ciudad_pk)
        .outerjoin(ciudad_destino, CondicionFlete.codigo_ciudad_destino_fk == ciudad_destino.codigo_ciudad_pk)
        .outerjoin(Zona, CondicionFlete.codigo_zona_fk == Zona.codigo_zona_pk)
        .with_entities(
            CondicionFlete.codigo_condicion_flete_pk,
            CondicionFlete.codigo_cliente_fk,
            CondicionFlete.codigo_tercero_fk,
            Tercero.nombre_corto.label("tercero_nombre"),
            CondicionFlete.codigo_ciudad_origen_fk,
            ciudad_origen.nombre.label("ciudad_origen_nombre"),
            CondicionFlete.codigo_ciudad_destino_fk,
            ciudad_destino.nombre.label("ciudad_destino_nombre"),
            CondicionFlete.codigo_zona_fk,
            Zona.nombre.label("zona_nombre"),
            CondicionFlete.codigo_cobertura_fk,
            CondicionFlete.codigo_pago_fk,
            CondicionFlete.descuento_peso,
            CondicionFlete.descuento_unidad,
            CondicionFlete.peso_minimo,
            CondicionFlete.peso_minimo_guia,
            CondicionFlete.flete_minimo,
            CondicionFlete.flete_minimo_guia,
            CondicionFlete.vr_peso,
            CondicionFlete.vr_unidad,
        )
    )


@router.get("/lista", response_model=CondicionFleteListResponse)
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
    query = db.query(CondicionFlete)
    if codigo_tercero_fk is not None:
        query = query.filter(CondicionFlete.codigo_tercero_fk == codigo_tercero_fk)
    if codigo_ciudad_origen_fk is not None:
        query = query.filter(CondicionFlete.codigo_ciudad_origen_fk == codigo_ciudad_origen_fk)
    if codigo_ciudad_destino_fk is not None:
        query = query.filter(CondicionFlete.codigo_ciudad_destino_fk == codigo_ciudad_destino_fk)
    if codigo_zona_fk is not None:
        query = query.filter(CondicionFlete.codigo_zona_fk == codigo_zona_fk)
    if codigo_pago_fk is not None:
        query = query.filter(CondicionFlete.codigo_pago_fk == codigo_pago_fk)
    total = query.with_entities(func.count(CondicionFlete.codigo_condicion_flete_pk)).scalar()

    offset = (page - 1) * size
    items = (
        _con_nombres(query)
        .order_by(CondicionFlete.codigo_condicion_flete_pk.asc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return CondicionFleteListResponse(total=total, page=page, size=size, items=items)


@router.post(
    "/liquidar",
    response_model=CondicionFleteLiquidarResponse,
    description="Busca la condición del tercero que aplica para liquidar (replica apiWindowsLiquidar de PHP).",
)
def liquidar(payload: CondicionFleteLiquidarRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    resultado = guia_service.buscar_condicion_flete(
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


@router.get("/detalle/{codigo_condicion_flete_pk}", response_model=CondicionFleteResponse)
def detalle(codigo_condicion_flete_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    condicion_flete = _con_nombres(db.query(CondicionFlete).filter(CondicionFlete.codigo_condicion_flete_pk == codigo_condicion_flete_pk)).first()

    if not condicion_flete:
        raise HTTPException(status_code=404, detail="Condición flete no encontrada")

    return condicion_flete

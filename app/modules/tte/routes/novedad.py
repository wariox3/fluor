from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tte.models.novedad import Novedad
from app.modules.tte.models.guia import Guia
from app.modules.tte.schemas.novedad import NovedadListResponse

router = APIRouter()


@router.get("/lista", response_model=NovedadListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    codigo_novedad_tipo_fk: Optional[str] = None,
    codigo_guia_fk: Optional[int] = None,
    codigo_tercero_fk: Optional[int] = None,
    codigo_despacho_fk: Optional[int] = None,
    estado_reporte: Optional[bool] = None,
    estado_atendido: Optional[bool] = None,
    estado_solucion: Optional[bool] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Novedad)
    if codigo_tercero_fk is not None:
        query = query.join(Guia, Novedad.codigo_guia_fk == Guia.codigo_guia_pk).filter(
            Guia.codigo_tercero_fk == codigo_tercero_fk
        )
    if codigo_novedad_tipo_fk is not None:
        query = query.filter(Novedad.codigo_novedad_tipo_fk == codigo_novedad_tipo_fk)
    if codigo_guia_fk is not None:
        query = query.filter(Novedad.codigo_guia_fk == codigo_guia_fk)
    if codigo_despacho_fk is not None:
        query = query.filter(Novedad.codigo_despacho_fk == codigo_despacho_fk)
    if estado_reporte is not None:
        query = query.filter(Novedad.estado_reporte == estado_reporte)
    if estado_atendido is not None:
        query = query.filter(Novedad.estado_atendido == estado_atendido)
    if estado_solucion is not None:
        query = query.filter(Novedad.estado_solucion == estado_solucion)
    if fecha_desde is not None:
        query = query.filter(Novedad.fecha >= fecha_desde)
    if fecha_hasta is not None:
        query = query.filter(Novedad.fecha <= fecha_hasta)
    total = query.with_entities(func.count(Novedad.codigo_novedad_pk)).scalar()
    offset = (page - 1) * size
    novedades = query.order_by(Novedad.codigo_novedad_pk.desc()).offset(offset).limit(size).all()
    return NovedadListResponse(total=total, page=page, size=size, items=novedades)

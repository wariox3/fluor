"""
Consignas del portal de clientes.

Reemplaza la API de holmio que consumía terbio (`Cliente/Operacion/ConsignaController`):
- `/turno/api/operacion/consigna/lista` → `GET /tur/consigna/lista-cliente`

Como holmio, el cliente ve las consignas de sus puestos (`tur_puesto.codigo_tercero_fk`) y las
consignas generales, que no tienen puesto. Además solo las habilitadas para el portal, igual que
`lista-portal`.

El modelo `Puesto` no mapea `codigo_tercero_fk`; para no modificarlo, el filtro usa una tabla
ligera (`table()`), que no se registra en los modelos.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import column, func, or_, select, table
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.tur.models.consigna import Consigna
from app.modules.tur.schemas.consigna import ConsignaListResponse

router = APIRouter()

# Solo las columnas de `tur_puesto` que necesita el filtro por cliente
_puesto = table("tur_puesto", column("codigo_puesto_pk"), column("codigo_tercero_fk"))


def _query_cliente(db: Session, tercero_id: int):
    """Consignas habilitadas de los puestos del cliente y las generales."""
    puestos_del_cliente = select(_puesto.c.codigo_puesto_pk).where(_puesto.c.codigo_tercero_fk == tercero_id)
    return (
        db.query(Consigna)
        .options(joinedload(Consigna.puesto_rel))
        .filter(
            Consigna.habilitado_portal.is_(True),
            or_(
                Consigna.codigo_puesto_fk.in_(puestos_del_cliente),
                Consigna.codigo_puesto_fk.is_(None),
            ),
        )
    )


@router.get("/lista-cliente", response_model=ConsignaListResponse)
def lista_cliente(
    tercero_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = _query_cliente(db, tercero_id)

    total = query.with_entities(func.count(Consigna.codigo_consigna_pk)).scalar()
    offset = (page - 1) * size
    items = (
        query
        # Como holmio, agrupadas por puesto; las generales (sin puesto) quedan primero
        .order_by(Consigna.codigo_puesto_fk.asc(), Consigna.codigo_consigna_pk.asc())
        .offset(offset)
        .limit(size)
        .all()
    )

    return ConsignaListResponse(total=total, page=page, size=size, items=items)

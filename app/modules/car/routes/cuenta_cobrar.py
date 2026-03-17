from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import date
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.car.schemas.cuenta_cobrar import CuentaCobrarItem, CuentaCobrarPendienteResponse

router = APIRouter()

BASE_SQL = """
SELECT
    cc.codigo_cuenta_cobrar_pk,
    cc.numero_documento,
    cc.numero_referencia,
    cc.fecha,
    cc.fecha_vence,
    cc.vr_subtotal,
    cc.vr_saldo_original,
    cc.vr_saldo,
    cc.vr_saldo_operado,
    cc.vr_abono,
    cc.plazo,
    cc.codigo_tercero_fk,
    cc.codigo_clasificacion_fk,
    cct.nombre as cuenta_cobrar_tipo_nombre,
    t.nombre_corto as tercero_nombre_corto,
    t.numero_identificacion as tercero_numero_identificacion,
    cla.nombre as clasificacion_nombre
FROM
    car_cuenta_cobrar cc
LEFT JOIN car_cuenta_cobrar_tipo cct ON cc.codigo_cuenta_cobrar_tipo_fk = cct.codigo_cuenta_cobrar_tipo_pk
LEFT JOIN gen_tercero t ON cc.codigo_tercero_fk = t.codigo_tercero_pk
LEFT JOIN car_clasificacion cla ON cc.codigo_clasificacion_fk = cla.codigo_clasificacion_pk
WHERE
    cc.vr_saldo > 0"""


@router.get("/pendiente", response_model=CuentaCobrarPendienteResponse)
def pendiente(
    page: int = 1,
    size: int = 50,
    tercero_id: Optional[int] = None,
    clasificacion_id: Optional[str] = None,
    vencidas: Optional[bool] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    numero_documento: Optional[str] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    conditions = []
    params = {}

    if tercero_id is not None:
        conditions.append("cc.codigo_tercero_fk = :tercero_id")
        params["tercero_id"] = tercero_id
    if clasificacion_id is not None:
        conditions.append("cc.codigo_clasificacion_fk = :clasificacion_id")
        params["clasificacion_id"] = clasificacion_id
    if vencidas is True:
        conditions.append("cc.fecha_vence < CURDATE()")
    if fecha_desde is not None:
        conditions.append("cc.fecha >= :fecha_desde")
        params["fecha_desde"] = fecha_desde
    if fecha_hasta is not None:
        conditions.append("cc.fecha <= :fecha_hasta")
        params["fecha_hasta"] = fecha_hasta
    if numero_documento is not None:
        conditions.append("cc.numero_documento LIKE :numero_documento")
        params["numero_documento"] = f"%{numero_documento}%"

    where_extra = (" AND " + " AND ".join(conditions)) if conditions else ""

    total = db.execute(
        text(f"SELECT COUNT(*) FROM car_cuenta_cobrar cc WHERE cc.vr_saldo > 0{where_extra}"),
        params,
    ).scalar()

    params["limit"] = size
    params["offset"] = (page - 1) * size
    rows = db.execute(
        text(f"{BASE_SQL}{where_extra} ORDER BY cc.fecha ASC LIMIT :limit OFFSET :offset"),
        params,
    ).mappings().all()

    return CuentaCobrarPendienteResponse(
        total=total, page=page, size=size, items=[CuentaCobrarItem(**row) for row in rows]
    )

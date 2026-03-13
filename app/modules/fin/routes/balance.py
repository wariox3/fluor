from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.fin.schemas.balance import CuentaBalanceItem

router = APIRouter()

SQL_BALANCE_CUENTA = text("""
WITH saldos_anteriores AS (
    SELECT
        c.codigo_cuenta_pk  AS codigo_cuenta_fk,
        c.nombre,
        COALESCE(SUM(s.vr_debito), 0) - COALESCE(SUM(s.vr_credito), 0) AS vr_saldo_anterior
    FROM fin_cuenta c
    LEFT JOIN fin_saldo_cuenta s
        ON s.codigo_cuenta_fk = c.codigo_cuenta_pk
        AND s.codigo_periodo_fk < :periodo_inicio
    GROUP BY c.codigo_cuenta_pk, c.nombre
),
movimientos_periodo AS (
    SELECT
        codigo_cuenta_fk,
        SUM(vr_debito)  AS vr_debito,
        SUM(vr_credito) AS vr_credito
    FROM fin_movimiento
    WHERE codigo_periodo_fk BETWEEN :periodo_inicio AND :periodo_fin
    GROUP BY codigo_cuenta_fk
)
SELECT
    sa.codigo_cuenta_fk,
    sa.nombre,
    sa.vr_saldo_anterior,
    COALESCE(mp.vr_debito,  0) AS vr_debito,
    COALESCE(mp.vr_credito, 0) AS vr_credito,
    sa.vr_saldo_anterior
    + COALESCE(mp.vr_debito,  0)
    - COALESCE(mp.vr_credito, 0) AS vr_saldo_cuenta
FROM saldos_anteriores sa
LEFT JOIN movimientos_periodo mp
    ON mp.codigo_cuenta_fk = sa.codigo_cuenta_fk
WHERE
    sa.vr_saldo_anterior          != 0
    OR COALESCE(mp.vr_debito,  0) != 0
    OR COALESCE(mp.vr_credito, 0) != 0
ORDER BY sa.codigo_cuenta_fk
""")


@router.get("/cuenta", response_model=List[CuentaBalanceItem])
def cuenta(periodo_inicio: int, periodo_fin: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user),):
    rows = db.execute(SQL_BALANCE_CUENTA, {"periodo_inicio": periodo_inicio, "periodo_fin": periodo_fin}).mappings().all()
    return [CuentaBalanceItem(**row) for row in rows]

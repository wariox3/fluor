"""
Impresión de recibos del portal de clientes.

Reemplaza la API de holmio que consumía terbio (`Cliente/Cartera/ReciboController`):
- `/api/cartera/recibo/imprimir` → `GET /imprimir-portal/{codigo_movimiento_pk}`

Holmio no validaba que el recibo fuera del cliente; aquí uno de otro cliente, o que el cliente no ve
en su lista (sin aprobar o anulado), responde 404. Como holmio, los recibos de caja (`RC`) y los
anticipos (`AN`) tienen formato; holmio no guardaba el del anticipo para el portal, así que desde
terbio no se podía imprimir. Los demás movimientos responden 409.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.car.formats import recibo_pdf

router = APIRouter()

_MOVIMIENTO_SQL = text("""
SELECT
    m.codigo_movimiento_pk,
    m.codigo_movimiento_clase_fk,
    mt.nombre AS movimiento_tipo,
    m.numero,
    m.fecha,
    m.fecha_documento,
    m.vr_total_neto,
    m.estado_aprobado,
    m.estado_anulado,
    m.comentarios,
    m.usuario,
    t.nombre_corto AS tercero_nombre_corto,
    t.numero_identificacion AS tercero_numero_identificacion,
    t.direccion AS tercero_direccion,
    t.telefono AS tercero_telefono,
    cu.cuenta AS cuenta_cuenta,
    cu.codigo_cuenta_contable_fk AS cuenta_codigo_cuenta_contable_fk,
    ba.nombre AS banco_nombre
FROM car_movimiento m
LEFT JOIN car_movimiento_tipo mt ON m.codigo_movimiento_tipo_fk = mt.codigo_movimiento_tipo_pk
LEFT JOIN gen_tercero t ON m.codigo_tercero_fk = t.codigo_tercero_pk
LEFT JOIN gen_cuenta cu ON m.codigo_cuenta_fk = cu.codigo_cuenta_pk
LEFT JOIN gen_banco ba ON cu.codigo_banco_fk = ba.codigo_banco_pk
WHERE m.codigo_movimiento_pk = :codigo_movimiento_pk
  AND m.codigo_tercero_fk = :tercero_id
  AND m.estado_aprobado = 1
  AND (m.estado_anulado = 0 OR m.estado_anulado IS NULL)
""")

# Como `CarMovimientoDetalleRepository::listaFormato` de holmio, en el orden en que se registraron
_DETALLES_SQL = text("""
SELECT
    d.codigo_cuenta_cobrar_tipo_fk,
    d.numero,
    t.numero_identificacion AS tercero_numero_identificacion,
    t.nombre_corto AS tercero_nombre_corto,
    d.codigo_cuenta_fk,
    d.naturaleza,
    d.vr_pago
FROM car_movimiento_detalle d
LEFT JOIN gen_tercero t ON d.codigo_tercero_fk = t.codigo_tercero_pk
WHERE d.codigo_movimiento_fk = :codigo_movimiento_pk
ORDER BY d.codigo_movimiento_detalle_pk
""")

_RESPUESTA_PDF = {
    200: {"content": {"application/pdf": {}}, "description": "Archivo PDF"},
    404: {"description": "El recibo no existe o el cliente no lo ve"},
    409: {"description": "El movimiento no tiene formato de impresión"},
}


@router.get(
    "/imprimir-portal/{codigo_movimiento_pk}",
    response_class=Response,
    responses=_RESPUESTA_PDF,
    description="PDF del recibo de caja o del anticipo del cliente, con las cuentas que afecta.",
)
def imprimir_portal(
    codigo_movimiento_pk: int,
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    fila = db.execute(
        _MOVIMIENTO_SQL, {"codigo_movimiento_pk": codigo_movimiento_pk, "tercero_id": tercero_id}
    ).mappings().first()
    if not fila:
        raise HTTPException(status_code=404, detail="Recibo no encontrado")
    movimiento = recibo_pdf.DatosMovimiento(**fila)
    if movimiento.codigo_movimiento_clase_fk not in recibo_pdf.CLASES_CON_FORMATO:
        raise HTTPException(status_code=409, detail="Este movimiento no tiene formato de impresión")

    detalles = [
        recibo_pdf.DetalleMovimiento(**d)
        for d in db.execute(_DETALLES_SQL, {"codigo_movimiento_pk": codigo_movimiento_pk}).mappings()
    ]
    # Holmio solo imprime la fecha de elaboración si la empresa contabiliza con ella
    contabilizar_fecha = db.execute(
        text("SELECT contabilizar_fecha_movimiento FROM gen_configuracion LIMIT 1")
    ).scalar()

    pdf_bytes = recibo_pdf.generar(movimiento, detalles, db, bool(contabilizar_fecha))
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=recibo_{codigo_movimiento_pk}.pdf"},
    )

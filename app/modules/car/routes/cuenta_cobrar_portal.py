"""
Estado de cuenta formal del portal de clientes.

Reemplaza el botón "Estado cuenta formal" de terbio (`Cliente/Cartera/CarteraController`), que
consultaba `/cartera/api/cuentapendiente` de holmio y armaba el PDF en terbio:
- `GET /estado-cuenta-portal`

Incluye todas las cuentas del cliente con saldo, sin los filtros de la lista, ordenadas por fecha
como `CarCuentaCobrarRepository::apiPendientes` de holmio.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.core.utils import ahora_local
from app.modules.car.formats import estado_cuenta_pdf
from app.modules.gen.models.configuracion import Configuracion
from app.modules.gen.models.imagen import Imagen
from app.modules.gen.models.tercero import Tercero

router = APIRouter()

_PENDIENTES_SQL = text("""
SELECT
    cct.nombre AS tipo,
    cc.numero_documento,
    cc.fecha,
    cc.fecha_vence,
    cc.plazo,
    cc.vr_saldo
FROM car_cuenta_cobrar cc
LEFT JOIN car_cuenta_cobrar_tipo cct ON cc.codigo_cuenta_cobrar_tipo_fk = cct.codigo_cuenta_cobrar_tipo_pk
WHERE cc.codigo_tercero_fk = :tercero_id
  AND cc.vr_saldo > 0
ORDER BY cc.fecha, cc.codigo_cuenta_cobrar_pk
""")


def _empresa(db: Session) -> estado_cuenta_pdf.Empresa:
    """Datos de la empresa para la carta; el logo es el de los demás formatos de fluor."""
    config = db.query(Configuracion).options(joinedload(Configuracion.ciudad_rel)).first()
    imagen = db.get(Imagen, "LOGO")
    logo = (imagen.imagen if imagen else None) or (config.logo if config else None)
    return estado_cuenta_pdf.Empresa(
        nombre=config.nombre if config else None,
        telefono=config.telefono if config else None,
        ciudad=config.ciudad_rel.nombre if config and config.ciudad_rel else None,
        logo=bytes(logo) if logo else None,
    )


@router.get(
    "/estado-cuenta-portal",
    response_class=Response,
    responses={
        200: {"content": {"application/pdf": {}}, "description": "Archivo PDF"},
        404: {"description": "El cliente no existe"},
    },
    description="Carta de estado de cuenta con las cuentas por cobrar del cliente con saldo.",
)
def estado_cuenta_portal(
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    tercero = db.get(Tercero, tercero_id)
    if not tercero:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    cuentas = [
        estado_cuenta_pdf.CuentaPendiente(**fila)
        for fila in db.execute(_PENDIENTES_SQL, {"tercero_id": tercero_id}).mappings()
    ]
    cliente = estado_cuenta_pdf.Cliente(
        nombre_corto=tercero.nombre_corto,
        numero_identificacion=tercero.numero_identificacion,
    )

    pdf_bytes = estado_cuenta_pdf.generar(_empresa(db), cliente, cuentas, ahora_local().date())
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=estado_cuenta_{tercero_id}.pdf"},
    )

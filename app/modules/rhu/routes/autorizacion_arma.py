"""
Autorización para portar armas del portal de clientes.

Reemplaza las APIs de holmio que consumía terbio (`Cliente/RecursoHumano/AutorizacionArmaController`):
- `/recursohumano/api/autorizacionarma/listatodos` → `GET /lista-portal`
- `/recursohumano/api/autorizacionarma/formato` → `GET /imprimir-portal/{codigo_empleado_pk}`
- `/recursohumano/api/autorizacionarma/formatotodos` → `GET /imprimir-portal-todos`

El cliente solo ve los empleados cuyo contrato actual es suyo (`rhu_contrato.codigo_tercero_fk`).
Holmio no validaba el cliente al imprimir uno, y "imprimir todos" sacaba los vigentes de todos los
clientes; aquí ambos se limitan al cliente.

El texto del PDF es el formato 14 de `gen_formato` (`contenido`, con los marcadores de holmio).
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.gen.models.configuracion import Configuracion
from app.modules.gen.models.formato import Formato
from app.modules.gen.models.formato_imagen import FormatoImagen
from app.modules.rhu.formats import autorizacion_arma_pdf
from app.modules.rhu.formats.autorizacion_arma_pdf import DatosEmpleado, DatosEmpresa
from app.modules.rhu.models.contrato import Contrato
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.models.poligono import Poligono
from app.modules.rhu.models.poligono_detalle import PoligonoDetalle
from app.modules.rhu.schemas.autorizacion_arma import (
    AutorizacionArmaPortalListResponse,
    AutorizacionArmaPortalResponse,
)

# Formato de holmio con el texto de la autorización
CODIGO_FORMATO = 14

# La impresión devuelve el PDF en bruto, no JSON; esto lo declara así en OpenAPI.
_RESPUESTA_PDF = {
    200: {
        "description": "Archivo PDF",
        "content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}},
    }
}

router = APIRouter()


def _query_portal(db: Session, tercero_id: int):
    """Empleados cuyo contrato actual es del cliente, con su cargo."""
    return (
        db.query(Empleado)
        .join(Contrato, Empleado.codigo_contrato_fk == Contrato.codigo_contrato_pk)
        .options(joinedload(Empleado.contrato_rel).joinedload(Contrato.cargo_rel))
        .filter(Contrato.codigo_tercero_fk == tercero_id)
    )


def _filtro_vigentes(hoy: date):
    """Como holmio: acreditación, polígono y psicofísico vigentes hoy."""
    return (
        Empleado.fecha_acreditacion >= hoy,
        Empleado.fecha_poligono >= hoy,
        Empleado.fecha_psicofisico >= hoy,
    )


def _vigente(empleado: Empleado, hoy: date) -> bool:
    fechas = (empleado.fecha_acreditacion, empleado.fecha_poligono, empleado.fecha_psicofisico)
    return all(fecha is not None and fecha >= hoy for fecha in fechas)


def _armas(db: Session, empleados: list[Empleado]) -> dict[int, list[tuple[str, float | None]]]:
    """Armas del polígono más reciente de cada empleado, en una sola consulta."""
    codigos = [e.codigo_empleado_pk for e in empleados]
    poligonos = (
        db.query(Poligono)
        .options(selectinload(Poligono.detalles).joinedload(PoligonoDetalle.arma_rel))
        .filter(Poligono.codigo_empleado_fk.in_(codigos))
        .order_by(Poligono.codigo_poligono_pk.asc())
        .all()
    )
    armas = {}
    # Al recorrerlos en orden, el último de cada empleado (el más reciente) prevalece
    for poligono in poligonos:
        armas[poligono.codigo_empleado_fk] = [
            (detalle.arma_rel.nombre or "", detalle.arma_rel.calibre)
            for detalle in poligono.detalles
            if detalle.arma_rel
        ]
    return armas


def _imprimir(db: Session, empleados: list[Empleado], nombre_archivo: str) -> Response:
    formato = db.query(Formato).filter(Formato.codigo_formato_pk == CODIGO_FORMATO).first()
    if not formato or not formato.contenido:
        raise HTTPException(status_code=409, detail="La empresa no tiene configurado el formato de autorización de armas")
    imagenes = db.query(FormatoImagen).filter(FormatoImagen.codigo_formato_fk == CODIGO_FORMATO).all()

    configuracion = db.query(Configuracion).options(joinedload(Configuracion.ciudad_rel)).first()

    def dato(campo: str) -> str:
        return (getattr(configuracion, campo, None) or "") if configuracion else ""

    ciudad = configuracion.ciudad_rel if configuracion else None
    empresa = DatosEmpresa(
        nombre=dato("nombre"),
        direccion=dato("direccion"),
        correo=dato("correo"),
        ciudad=ciudad.nombre if ciudad else "",
        # Holmio imprime el NIT sin dígito de verificación
        nit=dato("nit"),
    )

    armas = _armas(db, empleados)
    datos = [
        DatosEmpleado(
            nombre=e.nombre_corto or "",
            identificacion=e.numero_identificacion or "",
            cargo=e.cargo_nombre or "",
            fecha_desde_contrato=e.contrato_rel.fecha_desde if e.contrato_rel else None,
            armas=armas.get(e.codigo_empleado_pk, []),
        )
        for e in empleados
    ]
    pdf_bytes = autorizacion_arma_pdf.generar(datos, formato, imagenes, empresa)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={nombre_archivo}"},
    )


@router.get("/lista-portal", response_model=AutorizacionArmaPortalListResponse)
def lista_portal(
    tercero_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    """Empleados del cliente con sus fechas de acreditación, polígono y psicofísico."""
    query = _query_portal(db, tercero_id)

    total = query.with_entities(func.count(Empleado.codigo_empleado_pk)).scalar()
    offset = (page - 1) * size
    empleados = (
        query
        .order_by(Empleado.nombre_corto.asc(), Empleado.codigo_empleado_pk.asc())
        .offset(offset)
        .limit(size)
        .all()
    )

    hoy = date.today()
    items = [
        AutorizacionArmaPortalResponse(
            codigo_empleado_pk=e.codigo_empleado_pk,
            numero_identificacion=e.numero_identificacion,
            nombre_corto=e.nombre_corto,
            cargo_nombre=e.cargo_nombre,
            fecha_acreditacion=e.fecha_acreditacion,
            fecha_poligono=e.fecha_poligono,
            fecha_psicofisico=e.fecha_psicofisico,
            vigente=_vigente(e, hoy),
        )
        for e in empleados
    ]
    return AutorizacionArmaPortalListResponse(total=total, page=page, size=size, items=items)


@router.get(
    "/imprimir-portal-todos",
    response_class=Response,
    responses=_RESPUESTA_PDF,
    description="PDF con la autorización de los empleados del cliente con acreditación, polígono y psicofísico vigentes.",
)
def imprimir_portal_todos(
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    empleados = (
        _query_portal(db, tercero_id)
        .filter(*_filtro_vigentes(date.today()))
        .order_by(Empleado.nombre_corto.asc(), Empleado.codigo_empleado_pk.asc())
        .all()
    )
    if not empleados:
        raise HTTPException(status_code=404, detail="No hay empleados con la acreditación, el polígono y el psicofísico vigentes")
    return _imprimir(db, empleados, "autorizacion_arma.pdf")


@router.get(
    "/imprimir-portal/{codigo_empleado_pk}",
    response_class=Response,
    responses=_RESPUESTA_PDF,
    description="PDF de la autorización para portar armas de un empleado del cliente.",
)
def imprimir_portal(
    codigo_empleado_pk: int,
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    empleado = _query_portal(db, tercero_id).filter(Empleado.codigo_empleado_pk == codigo_empleado_pk).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return _imprimir(db, [empleado], f"autorizacion_arma_{codigo_empleado_pk}.pdf")

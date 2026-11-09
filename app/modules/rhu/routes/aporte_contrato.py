"""
Seguridad social del portal de clientes.

Reemplaza las APIs de holmio que consumía terbio (`Cliente/RecursoHumano/SeguridadSocial`):
- `/recursohumano/api/aporte/contrato/cliente` → `GET /lista-portal`
- `/api/documental/archivo/lista` (modelo `RhuAporteContrato`) → `GET /{id}/archivos`
- `/api/documental/archivo/descarga` → `GET /{id}/archivo/{archivo_id}/descargar`

El cliente solo ve los empleados cuyo contrato es suyo (`rhu_contrato.codigo_tercero_fk`) en
planillas no anuladas. Los soportes se cargan en holmio (ZIP por planilla) en `doc_archivo`.
"""

from urllib.parse import quote

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.backblaze import b2_client
from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.doc.models.archivo import Archivo
from app.modules.gen.models.configuracion import Configuracion
from app.modules.rhu.models.aporte import Aporte
from app.modules.rhu.models.aporte_contrato import AporteContrato
from app.modules.rhu.models.contrato import Contrato
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.schemas.aporte_contrato import (
    AporteContratoArchivoResponse,
    AporteContratoPortalListResponse,
    AporteContratoPortalResponse,
)

# Modelo con el que holmio registra los soportes de la planilla en `doc_archivo`
CODIGO_MODELO_ARCHIVO = "RhuAporteContrato"

router = APIRouter()


def _query_portal(db: Session, tercero_id: int):
    """Líneas de planilla no anuladas de los contratos del cliente."""
    return (
        db.query(AporteContrato)
        .join(Aporte, AporteContrato.codigo_aporte_fk == Aporte.codigo_aporte_pk)
        .join(Contrato, AporteContrato.codigo_contrato_fk == Contrato.codigo_contrato_pk)
        .filter(
            Contrato.codigo_tercero_fk == tercero_id,
            Aporte.estado_anulado == False,
        )
    )


def _aporte_contrato_del_cliente(db: Session, aporte_contrato_id: int, tercero_id: int) -> AporteContrato:
    aporte_contrato = (
        _query_portal(db, tercero_id)
        .filter(AporteContrato.codigo_aporte_contrato_pk == aporte_contrato_id)
        .first()
    )
    if not aporte_contrato:
        raise HTTPException(status_code=404, detail="Seguridad social no encontrada")
    return aporte_contrato


def _query_archivos(db: Session, aporte_contrato_id: int):
    return db.query(Archivo).filter(
        Archivo.codigo_archivo_tipo_fk == CODIGO_MODELO_ARCHIVO,
        Archivo.codigo == str(aporte_contrato_id),
    )


@router.get("/lista-portal", response_model=AporteContratoPortalListResponse)
def lista_portal(
    tercero_id: int,
    anio: int = Query(..., ge=2000, le=2100),
    mes: int = Query(..., ge=1, le=12),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    """Empleados del cliente en la planilla de seguridad social del periodo `anio`/`mes`."""
    query = _query_portal(db, tercero_id).filter(Aporte.anio == anio, Aporte.mes == mes)
    total = query.with_entities(func.count(AporteContrato.codigo_aporte_contrato_pk)).scalar()
    offset = (page - 1) * size
    aportes_contrato = (
        query
        .outerjoin(Empleado, AporteContrato.codigo_empleado_fk == Empleado.codigo_empleado_pk)
        .options(joinedload(AporteContrato.empleado_rel))
        .order_by(Empleado.nombre_corto.asc(), AporteContrato.codigo_aporte_contrato_pk.asc())
        .offset(offset)
        .limit(size)
        .all()
    )

    # Cantidad de soportes por línea, en una sola consulta para la página
    codigos = [str(ac.codigo_aporte_contrato_pk) for ac in aportes_contrato]
    archivos_por_codigo = {}
    if codigos:
        archivos_por_codigo = dict(
            db.query(Archivo.codigo, func.count(Archivo.codigo_archivo_pk))
            .filter(
                Archivo.codigo_archivo_tipo_fk == CODIGO_MODELO_ARCHIVO,
                Archivo.codigo.in_(codigos),
            )
            .group_by(Archivo.codigo)
            .all()
        )

    items = [
        AporteContratoPortalResponse(
            codigo_aporte_contrato_pk=ac.codigo_aporte_contrato_pk,
            codigo_aporte_fk=ac.codigo_aporte_fk,
            codigo_contrato_fk=ac.codigo_contrato_fk,
            codigo_empleado_fk=ac.codigo_empleado_fk,
            empleado_nombre=ac.empleado_nombre,
            numero_identificacion=ac.numero_identificacion,
            cantidad_archivos=archivos_por_codigo.get(str(ac.codigo_aporte_contrato_pk), 0),
        )
        for ac in aportes_contrato
    ]
    return AporteContratoPortalListResponse(total=total, page=page, size=size, items=items)


@router.get("/{aporte_contrato_id}/archivos", response_model=list[AporteContratoArchivoResponse])
def archivos(
    aporte_contrato_id: int,
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    """Soportes de la seguridad social de un empleado del cliente."""
    _aporte_contrato_del_cliente(db, aporte_contrato_id, tercero_id)
    return (
        _query_archivos(db, aporte_contrato_id)
        .order_by(Archivo.codigo_archivo_pk.desc())
        .all()
    )


@router.get("/{aporte_contrato_id}/archivo/{archivo_id}/descargar")
def descargar_archivo(
    aporte_contrato_id: int,
    archivo_id: int,
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    """Descarga desde Backblaze un soporte de la seguridad social de un empleado del cliente."""
    _aporte_contrato_del_cliente(db, aporte_contrato_id, tercero_id)
    archivo = (
        _query_archivos(db, aporte_contrato_id)
        .filter(Archivo.codigo_archivo_pk == archivo_id)
        .first()
    )
    if not archivo:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    configuracion = db.query(Configuracion).first()
    ruta_base = configuracion.ruta_almacenamiento_servicio if configuracion else None
    if not ruta_base:
        raise HTTPException(status_code=409, detail="La empresa no tiene configurado el almacenamiento de archivos")
    ruta = f"{ruta_base}/archivo/{archivo.codigo_archivo_pk}.{archivo.extension_original}"

    try:
        contenido, content_type = b2_client.download_file(ruta)
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 404:
            raise HTTPException(status_code=404, detail="El archivo no está en el almacenamiento") from error
        raise HTTPException(status_code=502, detail="Error al descargar el archivo desde el almacenamiento") from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="Error al descargar el archivo desde el almacenamiento") from error

    # En holmio `nombre` ya trae la extensión (es el nombre del archivo dentro del ZIP)
    nombre = archivo.nombre or f"{archivo.codigo_archivo_pk}.{archivo.extension_original}"
    return Response(
        content=contenido,
        media_type=archivo.tipo or content_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(nombre)}"},
    )

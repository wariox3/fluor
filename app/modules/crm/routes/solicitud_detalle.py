"""
Detalle de una PQRS (solicitud) del portal de clientes.

Reemplaza las APIs de holmio que consumía terbio (`Cliente/Crm/SolicitudContorller`):
- `/crm/api/gestion/solicitud/detalle` → `GET /detalle-portal/{codigo_solicitud_pk}`
- `/crm/api/solicitud/archivos` → `GET /{codigo_solicitud_pk}/archivos`
- `/api/documental/archivo/descarga` → `GET /{codigo_solicitud_pk}/archivo/{archivo_id}/descargar`

Holmio no validaba que la PQRS fuera del cliente; aquí una de otro cliente responde 404. Como en las
visitas, los archivos son los que holmio carga a la PQRS en `doc_archivo` (modelo `CrmSolicitud`) y
que la empresa marcó para el portal (`portal_clientes`); terbio mostraba todos.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.crm.models.solicitud import Solicitud
from app.modules.crm.models.solicitud_analisis import SolicitudAnalisis
from app.modules.crm.models.solicitud_respuesta import SolicitudRespuesta
from app.modules.crm.models.solicitud_seguimiento import SolicitudSeguimiento
from app.modules.crm.models.solicitud_tema import SolicitudTema
from app.modules.crm.routes.solicitud import _query_portal
from app.modules.crm.schemas.solicitud_detalle import (
    SolicitudAnalisisPortalResponse,
    SolicitudPortalDetalleResponse,
    SolicitudRespuestaPortalResponse,
    SolicitudSeguimientoPortalResponse,
)
from app.modules.doc.models.archivo import Archivo
from app.modules.doc.schemas.archivo import ArchivoResponse
from app.modules.doc.services import archivo as archivo_service

# Modelo con el que holmio registra los archivos de la PQRS en `doc_archivo`
CODIGO_MODELO_ARCHIVO = "CrmSolicitud"

router = APIRouter()


def _solicitud_del_cliente(db: Session, codigo_solicitud_pk: int, tercero_id: int) -> Solicitud:
    """PQRS con sus nombres; 404 si no existe o es de otro cliente."""
    solicitud = (
        _query_portal(db, tercero_id)
        .filter(Solicitud.codigo_solicitud_pk == codigo_solicitud_pk)
        .first()
    )
    if not solicitud:
        raise HTTPException(status_code=404, detail="PQRS no encontrada")
    return solicitud


def _query_archivos(db: Session, codigo_solicitud_pk: int):
    # El cliente solo ve los que la empresa marcó para el portal
    return archivo_service.query_archivos(db, CODIGO_MODELO_ARCHIVO, codigo_solicitud_pk, solo_portal=True)


@router.get("/detalle-portal/{codigo_solicitud_pk}", response_model=SolicitudPortalDetalleResponse)
def detalle_portal(
    codigo_solicitud_pk: int,
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    """PQRS con su análisis, seguimientos y respuestas, en el orden en que se registraron."""
    solicitud = _solicitud_del_cliente(db, codigo_solicitud_pk, tercero_id)

    tema = (
        db.get(SolicitudTema, solicitud.codigo_solicitud_tema_fk)
        if solicitud.codigo_solicitud_tema_fk
        else None
    )
    analisis = (
        db.query(SolicitudAnalisis)
        .filter(SolicitudAnalisis.codigo_solicitud_fk == codigo_solicitud_pk)
        .order_by(SolicitudAnalisis.codigo_solicitud_analisis_pk)
        .all()
    )
    seguimientos = (
        db.query(SolicitudSeguimiento)
        .filter(SolicitudSeguimiento.codigo_solicitud_fk == codigo_solicitud_pk)
        .order_by(SolicitudSeguimiento.codigo_solicitud_seguimiento_pk)
        .all()
    )
    respuestas = (
        db.query(SolicitudRespuesta)
        .filter(SolicitudRespuesta.codigo_solicitud_fk == codigo_solicitud_pk)
        .order_by(SolicitudRespuesta.codigo_solicitud_respuesta_pk)
        .all()
    )

    # `model_copy` no valida: los registros van ya convertidos a sus schemas
    return SolicitudPortalDetalleResponse.model_validate(solicitud).model_copy(
        update={
            "tema_nombre": tema.nombre if tema else None,
            "analisis": [SolicitudAnalisisPortalResponse.model_validate(a) for a in analisis],
            "seguimientos": [SolicitudSeguimientoPortalResponse.model_validate(s) for s in seguimientos],
            "respuestas": [SolicitudRespuestaPortalResponse.model_validate(r) for r in respuestas],
            "cantidad_archivos": _query_archivos(db, codigo_solicitud_pk).count(),
        }
    )


@router.get("/{codigo_solicitud_pk}/archivos", response_model=list[ArchivoResponse])
def archivos(
    codigo_solicitud_pk: int,
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    """Archivos que la empresa cargó a la PQRS del cliente."""
    _solicitud_del_cliente(db, codigo_solicitud_pk, tercero_id)
    return _query_archivos(db, codigo_solicitud_pk).order_by(Archivo.codigo_archivo_pk.desc()).all()


@router.get("/{codigo_solicitud_pk}/archivo/{archivo_id}/descargar")
def descargar_archivo(
    codigo_solicitud_pk: int,
    archivo_id: int,
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    """Descarga desde Backblaze un archivo de la PQRS del cliente."""
    _solicitud_del_cliente(db, codigo_solicitud_pk, tercero_id)
    archivo = _query_archivos(db, codigo_solicitud_pk).filter(Archivo.codigo_archivo_pk == archivo_id).first()
    if not archivo:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return archivo_service.descargar(db, archivo)

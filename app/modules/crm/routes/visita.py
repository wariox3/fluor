"""
Visitas del portal de clientes.

Reemplaza las APIs de holmio que consumía terbio (`Cliente/Crm/VisitaController`):
- `/crm/api/gestion/visita/lista` → `GET /lista-portal`
- `/crm/api/gestion/visita/detalle` → `GET /detalle-portal/{codigo_visita_pk}`
- `/crm/api/gestion/visita/formato` → `GET /imprimir-portal/{codigo_visita_pk}`
- `/crm/api/gestion/visita/lista/archivos` → `GET /{codigo_visita_pk}/archivos`
- `/api/documental/archivo/descarga` → `GET /{codigo_visita_pk}/archivo/{archivo_id}/descargar`

El cliente solo ve las visitas registradas a su nombre (`crm_visita.codigo_tercero_fk`).
Holmio no lo validaba en el detalle ni en el formato; aquí una visita de otro cliente responde 404.

Los archivos son los que holmio carga a la visita en `doc_archivo` (modelo `CrmVisita`) y que la
empresa marcó para el portal (`portal_clientes`); terbio mostraba todos. No incluyen los de sus
reportes y compromisos.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.modules.crm.formats import visita_pdf
from app.modules.crm.models.visita import Visita
from app.modules.crm.schemas.visita import (
    VisitaPortalDetalleResponse,
    VisitaPortalListResponse,
)
from app.modules.doc.models.archivo import Archivo
from app.modules.doc.schemas.archivo import ArchivoResponse
from app.modules.doc.services import archivo as archivo_service

# Modelo con el que holmio registra los archivos de la visita en `doc_archivo`
CODIGO_MODELO_ARCHIVO = "CrmVisita"

# La impresión devuelve el PDF en bruto, no JSON; esto lo declara así en OpenAPI.
_RESPUESTA_PDF = {
    200: {
        "description": "Archivo PDF",
        "content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}},
    }
}

router = APIRouter()


def _query_portal(db: Session, tercero_id: int):
    """Visitas del cliente, con el tipo, el motivo y el asesor."""
    return (
        db.query(Visita)
        .options(
            joinedload(Visita.visita_tipo_rel),
            joinedload(Visita.visita_motivo_rel),
            joinedload(Visita.asesor_rel),
        )
        .filter(Visita.codigo_tercero_fk == tercero_id)
    )


def _visita_del_cliente(db: Session, codigo_visita_pk: int, tercero_id: int) -> Visita:
    """Visita con sus compromisos y reportes; 404 si no existe o es de otro cliente."""
    visita = (
        _query_portal(db, tercero_id)
        .options(selectinload(Visita.compromisos), selectinload(Visita.reportes))
        .filter(Visita.codigo_visita_pk == codigo_visita_pk)
        .first()
    )
    if not visita:
        raise HTTPException(status_code=404, detail="Visita no encontrada")
    return visita


def _query_archivos(db: Session, codigo_visita_pk: int):
    # El cliente solo ve los que la empresa marcó para el portal
    return archivo_service.query_archivos(db, CODIGO_MODELO_ARCHIVO, codigo_visita_pk, solo_portal=True)


@router.get("/lista-portal", response_model=VisitaPortalListResponse)
def lista_portal(
    tercero_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = _query_portal(db, tercero_id)

    total = query.with_entities(func.count(Visita.codigo_visita_pk)).scalar()
    offset = (page - 1) * size
    items = (
        query
        # Como holmio, de la más reciente a la más antigua
        .order_by(Visita.fecha.desc(), Visita.codigo_visita_pk.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    return VisitaPortalListResponse(total=total, page=page, size=size, items=items)


@router.get("/detalle-portal/{codigo_visita_pk}", response_model=VisitaPortalDetalleResponse)
def detalle_portal(
    codigo_visita_pk: int,
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    visita = _visita_del_cliente(db, codigo_visita_pk, tercero_id)
    cantidad_archivos = _query_archivos(db, codigo_visita_pk).count()
    return VisitaPortalDetalleResponse.model_validate(visita).model_copy(
        update={"cantidad_archivos": cantidad_archivos}
    )


@router.get(
    "/imprimir-portal/{codigo_visita_pk}",
    response_class=Response,
    responses=_RESPUESTA_PDF,
    description="PDF del formato de la visita, con sus reportes y compromisos.",
)
def imprimir_portal(
    codigo_visita_pk: int,
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    visita = _visita_del_cliente(db, codigo_visita_pk, tercero_id)
    pdf_bytes = visita_pdf.generar(visita, db)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=visita_{codigo_visita_pk}.pdf"},
    )


@router.get("/{codigo_visita_pk}/archivos", response_model=list[ArchivoResponse])
def archivos(
    codigo_visita_pk: int,
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    """Archivos que la empresa cargó a la visita del cliente."""
    _visita_del_cliente(db, codigo_visita_pk, tercero_id)
    return _query_archivos(db, codigo_visita_pk).order_by(Archivo.codigo_archivo_pk.desc()).all()


@router.get("/{codigo_visita_pk}/archivo/{archivo_id}/descargar")
def descargar_archivo(
    codigo_visita_pk: int,
    archivo_id: int,
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    """Descarga desde Backblaze un archivo de la visita del cliente."""
    _visita_del_cliente(db, codigo_visita_pk, tercero_id)
    archivo = _query_archivos(db, codigo_visita_pk).filter(Archivo.codigo_archivo_pk == archivo_id).first()
    if not archivo:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return archivo_service.descargar(db, archivo)

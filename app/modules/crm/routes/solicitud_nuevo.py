"""
Registro de PQRS (solicitudes) desde el portal de clientes.

Reemplaza la API de holmio que consumía terbio (`Cliente/Crm/SolicitudContorller::nuevo`):
- `/crm/api/gestion/solicitud/nuevo` → `POST /nuevo-portal`
- Tipos de PQRS (en terbio, una lista fija en la plantilla) → `GET /tipo-portal`

Como en las cotizaciones, el tercero sale de la membresía del usuario y no del request. El canal es
siempre el portal (`POR`), como lo enviaba terbio. Holmio reemplazaba el teléfono digitado por el
del tercero; aquí el del tercero solo se usa si el cliente no digita uno.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.master_database import get_master_db
from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.core.utils import ahora_local
from app.modules.crm.models.canal import Canal
from app.modules.crm.models.solicitud import Solicitud
from app.modules.crm.models.solicitud_tipo import SolicitudTipo
from app.modules.crm.routes.cotizacion import _membresia_cliente
from app.modules.crm.routes.solicitud import _query_portal
from app.modules.crm.schemas.solicitud import SolicitudPortalResponse
from app.modules.crm.schemas.solicitud_nuevo import (
    SolicitudPortalNuevoRequest,
    SolicitudTipoPortalResponse,
)
from app.modules.gen.models.tercero import Tercero

# Canal con el que llegan las PQRS registradas por el cliente, como terbio
CANAL_PORTAL = "POR"

router = APIRouter()


@router.get("/tipo-portal", response_model=list[SolicitudTipoPortalResponse])
def tipo_portal(
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    """Tipos de PQRS habilitados para el portal de clientes, por nombre."""
    return (
        db.query(SolicitudTipo)
        .filter(SolicitudTipo.portal_clientes.is_(True))
        .order_by(SolicitudTipo.nombre)
        .all()
    )


@router.post("/nuevo-portal", response_model=SolicitudPortalResponse, status_code=201)
def nuevo_portal(
    payload: SolicitudPortalNuevoRequest,
    request: Request,
    db: Session = Depends(get_tenant_db),
    master_db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    """Registra una PQRS a nombre del cliente de la membresía, por el canal del portal."""
    tercero_id = _membresia_cliente(request, master_db, current_user).cliente_id

    tipo = db.get(SolicitudTipo, payload.codigo_solicitud_tipo_fk)
    if not tipo or not tipo.portal_clientes:
        raise HTTPException(status_code=404, detail="Tipo de PQRS no encontrado")
    if not db.get(Canal, CANAL_PORTAL):
        # Configuración de la empresa, no error del cliente
        raise HTTPException(status_code=500, detail="La empresa no tiene configurado el canal del portal")
    tercero = db.get(Tercero, tercero_id)
    if not tercero:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    telefono = payload.telefono_contacto or tercero.telefono or tercero.celular
    solicitud = Solicitud(
        codigo_solicitud_tipo_fk=tipo.codigo_solicitud_tipo_pk,
        codigo_tercero_fk=tercero_id,
        codigo_canal_fk=CANAL_PORTAL,
        descripcion=payload.descripcion,
        # Como holmio, solo la fecha de registro; la fecha de la PQRS la asigna quien la gestiona
        fecha_registro=ahora_local().date(),
        nombre_contacto=payload.nombre_contacto,
        numero_identificacion_contacto=payload.numero_identificacion_contacto,
        telefono_contacto=(telefono or "")[:50] or None,
        correo_contacto=payload.correo_contacto,
        cargo_contacto=payload.cargo_contacto,
        usuario=(current_user.get("email") or "")[:50] or None,
    )
    db.add(solicitud)
    db.commit()

    return (
        _query_portal(db, tercero_id)
        .filter(Solicitud.codigo_solicitud_pk == solicitud.codigo_solicitud_pk)
        .one()
    )

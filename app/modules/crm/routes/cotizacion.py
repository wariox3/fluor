"""
Cotizaciones del portal de clientes.

Reemplaza las APIs de holmio que consumía terbio (`Cliente/Crm/CotizacionController`):
- `/crm/api/comercial/cotizacion/lista` → `GET /lista-portal`
- `/crm/api/comercial/cotizaciontipo/lista` → `GET /tipo-portal`
- `/crm/api/comercial/cotizacion/nuevo` → `POST /nuevo-portal`
- `/crm/api/comercial/cotizacion/detalle` → `GET /detalle-portal/{codigo_cotizacion_pk}`
- `/crm/api/comercial/cotizacion/detalle/lista` → `GET /{codigo_cotizacion_pk}/detalles-portal`
- `/crm/api/comercial/cotizacion/detalle/nuevo` → `POST /{codigo_cotizacion_pk}/detalle-nuevo-portal`
- `/crm/api/comercial/cotizacion/detalle/eliminar` → `POST /{codigo_cotizacion_pk}/detalle-eliminar-portal`

El cliente solo ve las cotizaciones registradas a su nombre (`crm_cotizacion.codigo_tercero_fk`).
Al crear o modificar, el tercero sale de la membresía del usuario y no del request. Holmio no validaba
que los servicios a eliminar fueran de la cotización ni bloqueaba agregar servicios a una cotización
autorizada; aquí sí.

El ítem de los servicios es el que el control de la empresa configuró al usuario
(`mas_user_tenant_configuracion.codigo_item_cotizacion_fk`); en terbio era uno por empresa.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.master_database import get_master_db
from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.core.utils import ahora_local
from app.modules.crm.models.cotizacion import Cotizacion
from app.modules.crm.models.cotizacion_detalle import CotizacionDetalle
from app.modules.crm.models.cotizacion_tipo import CotizacionTipo
from app.modules.crm.schemas.cotizacion import (
    CotizacionDetallePortalEliminarRequest,
    CotizacionDetallePortalNuevoRequest,
    CotizacionDetallePortalResponse,
    CotizacionPortalDetalleResponse,
    CotizacionPortalListResponse,
    CotizacionPortalNuevoRequest,
    CotizacionTipoPortalResponse,
)
from app.modules.crm.services import cotizacion as cotizacion_service
from app.modules.gen.models.configuracion import Configuracion
from app.modules.gen.models.item import Item
from app.modules.mas.models.user_tenant import UserTenant
from app.modules.tur.models.modalidad import Modalidad
from app.modules.tur.models.sector import Sector

# Clase de los tipos de cotización que el cliente puede solicitar (vigilancia), como terbio
CLASE_COTIZACION_PORTAL = "VIG"
# Los servicios del portal se liquidan por mes
PERIODO_MENSUAL = "M"

router = APIRouter()


def _query_portal(db: Session, tercero_id: int):
    """Cotizaciones del cliente, con su tipo, asesor, forma de pago y negocio."""
    return (
        db.query(Cotizacion)
        .options(
            joinedload(Cotizacion.cotizacion_tipo_rel),
            joinedload(Cotizacion.tercero_rel),
            joinedload(Cotizacion.asesor_rel),
            joinedload(Cotizacion.forma_pago_rel),
            joinedload(Cotizacion.negocio_rel),
        )
        .filter(Cotizacion.codigo_tercero_fk == tercero_id)
    )


@router.get("/lista-portal", response_model=CotizacionPortalListResponse)
def lista_portal(
    tercero_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = _query_portal(db, tercero_id)

    total = query.with_entities(func.count(Cotizacion.codigo_cotizacion_pk)).scalar()
    offset = (page - 1) * size
    items = (
        query
        # Como holmio, de la más reciente a la más antigua
        .order_by(Cotizacion.codigo_cotizacion_pk.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    return CotizacionPortalListResponse(total=total, page=page, size=size, items=items)


def _membresia_cliente(request: Request, master_db: Session, current_user: dict) -> UserTenant:
    """Membresía del usuario como cliente en la empresa del request (X-Tenant-ID, ya validado por
    `get_tenant_db`). 403 si no entra como cliente o no tiene cliente asignado."""
    usuario = str(current_user.get("sub", ""))
    tenant = request.headers.get("X-Tenant-ID", "").strip()
    membresia = None
    if usuario.isdigit() and tenant.isdigit():
        membresia = (
            master_db.query(UserTenant)
            .filter(
                UserTenant.usuario_id == int(usuario),
                UserTenant.tenant_id == int(tenant),
                UserTenant.activo.is_(True),
                UserTenant.cliente.is_(True),
            )
            .first()
        )
    if not membresia or membresia.cliente_id is None:
        raise HTTPException(status_code=403, detail="Tu usuario no tiene un cliente asignado en esta empresa")
    return membresia


def _cotizacion_del_cliente(db: Session, codigo_cotizacion_pk: int, tercero_id: int) -> Cotizacion:
    """Cotización con sus nombres; 404 si no existe o es de otro cliente."""
    cotizacion = (
        _query_portal(db, tercero_id)
        .filter(Cotizacion.codigo_cotizacion_pk == codigo_cotizacion_pk)
        .first()
    )
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return cotizacion


def _validar_editable(cotizacion: Cotizacion) -> None:
    """Como holmio, una cotización autorizada (o anulada) ya no cambia sus servicios."""
    if cotizacion.estado_anulado:
        raise HTTPException(status_code=400, detail="La cotización está anulada")
    if cotizacion.estado_autorizado:
        raise HTTPException(status_code=400, detail="La cotización ya está autorizada")


def _query_detalles(db: Session, codigo_cotizacion_pk: int):
    return (
        db.query(CotizacionDetalle)
        .options(joinedload(CotizacionDetalle.item_rel), joinedload(CotizacionDetalle.modalidad_rel))
        .filter(CotizacionDetalle.codigo_cotizacion_fk == codigo_cotizacion_pk)
        .order_by(CotizacionDetalle.codigo_cotizacion_detalle_pk)
    )


@router.get("/tipo-portal", response_model=list[CotizacionTipoPortalResponse])
def tipo_portal(
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    """Tipos de cotización de vigilancia habilitados para el portal de clientes."""
    return (
        db.query(CotizacionTipo)
        .filter(
            CotizacionTipo.portal_clientes.is_(True),
            CotizacionTipo.codigo_cotizacion_clase_fk == CLASE_COTIZACION_PORTAL,
        )
        # Como holmio
        .order_by(CotizacionTipo.codigo_cotizacion_tipo_pk.desc())
        .all()
    )


@router.post("/nuevo-portal", response_model=CotizacionPortalDetalleResponse, status_code=201)
def nuevo_portal(
    payload: CotizacionPortalNuevoRequest,
    request: Request,
    db: Session = Depends(get_tenant_db),
    master_db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    """Crea una cotización a nombre del cliente de la membresía, sin servicios."""
    tercero_id = _membresia_cliente(request, master_db, current_user).cliente_id

    tipo = db.get(CotizacionTipo, payload.codigo_cotizacion_tipo_fk)
    if not tipo or not tipo.portal_clientes or tipo.codigo_cotizacion_clase_fk != CLASE_COTIZACION_PORTAL:
        raise HTTPException(status_code=404, detail="Tipo de cotización no encontrado")
    if not db.get(Sector, payload.codigo_sector_fk):
        raise HTTPException(status_code=404, detail="Sector no encontrado")

    configuracion = db.query(Configuracion.vr_salario_minimo_turno).first()
    hoy = ahora_local().date()
    cotizacion = Cotizacion(
        codigo_cotizacion_tipo_fk=tipo.codigo_cotizacion_tipo_pk,
        codigo_tercero_fk=tercero_id,
        codigo_sector_fk=payload.codigo_sector_fk,
        estrato=payload.estrato,
        comentarios=payload.comentarios,
        fecha=hoy,
        fecha_vence=hoy,
        vencimiento=hoy,
        vr_salario_base=(configuracion.vr_salario_minimo_turno if configuracion else None) or 0,
        usuario=(current_user.get("email") or "")[:50] or None,
    )
    db.add(cotizacion)
    db.commit()
    return _cotizacion_del_cliente(db, cotizacion.codigo_cotizacion_pk, tercero_id)


@router.get("/detalle-portal/{codigo_cotizacion_pk}", response_model=CotizacionPortalDetalleResponse)
def detalle_portal(
    codigo_cotizacion_pk: int,
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    return _cotizacion_del_cliente(db, codigo_cotizacion_pk, tercero_id)


@router.get("/{codigo_cotizacion_pk}/detalles-portal", response_model=list[CotizacionDetallePortalResponse])
def detalles_portal(
    codigo_cotizacion_pk: int,
    tercero_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    """Servicios cotizados, en el orden en que se agregaron."""
    _cotizacion_del_cliente(db, codigo_cotizacion_pk, tercero_id)
    return _query_detalles(db, codigo_cotizacion_pk).all()


@router.post(
    "/{codigo_cotizacion_pk}/detalle-nuevo-portal",
    response_model=CotizacionDetallePortalResponse,
    status_code=201,
)
def detalle_nuevo_portal(
    codigo_cotizacion_pk: int,
    payload: CotizacionDetallePortalNuevoRequest,
    request: Request,
    db: Session = Depends(get_tenant_db),
    master_db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    """Agrega un servicio mensual con el ítem configurado al usuario y reliquida la cotización."""
    membresia = _membresia_cliente(request, master_db, current_user)
    cotizacion = _cotizacion_del_cliente(db, codigo_cotizacion_pk, membresia.cliente_id)
    _validar_editable(cotizacion)

    codigo_item = membresia.configuracion.codigo_item_cotizacion_fk if membresia.configuracion else None
    if codigo_item is None:
        raise HTTPException(
            status_code=400,
            detail="Tu usuario no tiene un ítem para cotizar configurado. Comunícate con la empresa.",
        )
    item = db.get(Item, codigo_item)
    if not item:
        raise HTTPException(status_code=400, detail="El ítem para cotizar configurado a tu usuario no existe")
    if not db.get(Modalidad, payload.codigo_modalidad_fk):
        raise HTTPException(status_code=404, detail="Modalidad no encontrada")

    horas = cotizacion_service.hora_servicio(payload.hora_desde, payload.hora_hasta, payload.fecha_desde)
    impuesto = item.impuesto_iva_venta
    detalle = CotizacionDetalle(
        codigo_cotizacion_fk=cotizacion.codigo_cotizacion_pk,
        codigo_item_fk=item.codigo_item_pk,
        codigo_modalidad_fk=payload.codigo_modalidad_fk,
        cantidad=payload.cantidad,
        periodo=PERIODO_MENSUAL,
        fecha_desde=payload.fecha_desde,
        fecha_hasta=payload.fecha_hasta,
        hora_desde=payload.hora_desde,
        hora_hasta=payload.hora_hasta,
        lunes=payload.lunes,
        martes=payload.martes,
        miercoles=payload.miercoles,
        jueves=payload.jueves,
        viernes=payload.viernes,
        sabado=payload.sabado,
        domingo=payload.domingo,
        festivo=payload.festivo,
        horas_unidad=horas.horas,
        horas_diurnas_unidad=horas.diurnas,
        horas_nocturnas_unidad=horas.nocturnas,
        vr_salario_base=cotizacion.vr_salario_base or 0,
        codigo_impuesto_iva_fk=item.codigo_impuesto_iva_venta_fk,
        porcentaje_iva=impuesto.porcentaje if impuesto else 0,
        porcentaje_base_iva=impuesto.porcentaje_base if impuesto else 0,
    )
    detalle.horario = cotizacion_service.horario_turno(detalle)
    db.add(detalle)
    db.flush()
    cotizacion_service.liquidar_servicios(db, cotizacion)
    db.commit()
    return _query_detalles(db, cotizacion.codigo_cotizacion_pk).filter(
        CotizacionDetalle.codigo_cotizacion_detalle_pk == detalle.codigo_cotizacion_detalle_pk
    ).one()


@router.post("/{codigo_cotizacion_pk}/detalle-eliminar-portal", status_code=204)
def detalle_eliminar_portal(
    codigo_cotizacion_pk: int,
    payload: CotizacionDetallePortalEliminarRequest,
    request: Request,
    db: Session = Depends(get_tenant_db),
    master_db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    """Quita servicios de la cotización y la reliquida. Solo los de esa cotización."""
    membresia = _membresia_cliente(request, master_db, current_user)
    cotizacion = _cotizacion_del_cliente(db, codigo_cotizacion_pk, membresia.cliente_id)
    _validar_editable(cotizacion)

    detalles = (
        db.query(CotizacionDetalle)
        .filter(
            CotizacionDetalle.codigo_cotizacion_fk == cotizacion.codigo_cotizacion_pk,
            CotizacionDetalle.codigo_cotizacion_detalle_pk.in_(payload.ids),
        )
        .all()
    )
    if len(detalles) != len(set(payload.ids)):
        raise HTTPException(status_code=404, detail="Algunos servicios no pertenecen a la cotización")

    for detalle in detalles:
        db.delete(detalle)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="No se puede eliminar, el servicio se encuentra en uso en el sistema"
        ) from None
    cotizacion_service.liquidar_servicios(db, cotizacion)
    db.commit()

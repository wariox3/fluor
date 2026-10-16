import base64
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.core.backblaze import b2_client
from app.core.rate_limit import limiter
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.doc.models.fichero import Fichero
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.despacho import Despacho
from app.modules.tte.models.guia import Guia
from app.modules.tte.models.operacion import Operacion
from app.modules.tte.models.seguimiento import Seguimiento
from app.modules.tte.models.seguimiento_tipo import SeguimientoTipo
from app.modules.tte.schemas.seguimiento import SeguimientoCreateRequest, SeguimientoActualizarInterfaceRequest, SeguimientoResponse, SeguimientoListItemResponse, SeguimientoListResponse, SeguimientoDetalleGuiaResponse, SeguimientoDetalleArchivoResponse

router = APIRouter()

# La tabla supera los 18 millones de registros: el total de la lista se cuenta hasta este tope
TOPE_CONTEO_LISTA = 10000


@router.post("/nuevo", response_model=SeguimientoResponse)
def nuevo(payload: SeguimientoCreateRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    if not db.query(Guia).filter(Guia.codigo_guia_pk == payload.codigo_guia_fk).first():
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    if payload.codigo_seguimiento_tipo_fk is not None:
        if not db.query(SeguimientoTipo).filter(SeguimientoTipo.codigo_seguimiento_tipo_pk == payload.codigo_seguimiento_tipo_fk).first():
            raise HTTPException(status_code=404, detail="Tipo de seguimiento no encontrado")

    if payload.codigo_operacion_fk is not None:
        if not db.query(Operacion).filter(Operacion.codigo_operacion_pk == payload.codigo_operacion_fk).first():
            raise HTTPException(status_code=404, detail="Operación no encontrada")

    seguimiento = Seguimiento(
        codigo_guia_fk=payload.codigo_guia_fk,
        codigo_seguimiento_tipo_fk=payload.codigo_seguimiento_tipo_fk,
        codigo_operacion_fk=payload.codigo_operacion_fk,
        fecha=datetime.now(),
        fecha_seguimiento=payload.fecha_seguimiento or datetime.now(),
        usuario=current_user["sub"],
        comentario=payload.comentario,
        datos=payload.datos,
        latitud=payload.latitud,
        longitud=payload.longitud,
    )

    db.add(seguimiento)
    db.commit()
    db.refresh(seguimiento)

    return seguimiento


@router.get("/lista", response_model=SeguimientoListResponse)
@limiter.limit("10/minute")
def lista(
    request: Request,
    response: Response,
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=200),
    codigo_guia_fk: Optional[int] = None,
    codigo_seguimiento_tipo_fk: Optional[str] = None,
    codigo_operacion_fk: Optional[str] = None,
    estado_interface: Optional[bool] = None,
    estado_descartado: Optional[bool] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    fecha_desde_ingreso: Optional[date] = None,
    fecha_hasta_ingreso: Optional[date] = None,
    fecha_desde_despacho: Optional[date] = None,
    fecha_hasta_despacho: Optional[date] = None,
    guia_codigo_tercero_fk: Optional[int] = None,
    guia_estado_interface_soporte: Optional[bool] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Seguimiento)
    # Los filtros por datos de guía o despacho requieren los joins desde el conteo; sin registro asociado no hay coincidencia
    filtra_despacho = fecha_desde_despacho is not None or fecha_hasta_despacho is not None
    filtra_guia = filtra_despacho or fecha_desde_ingreso is not None or fecha_hasta_ingreso is not None or guia_codigo_tercero_fk is not None or guia_estado_interface_soporte is not None
    if filtra_guia:
        query = query.join(Guia, Seguimiento.codigo_guia_fk == Guia.codigo_guia_pk)
    if filtra_despacho:
        query = query.join(Despacho, Guia.codigo_despacho_fk == Despacho.codigo_despacho_pk)
    if guia_codigo_tercero_fk is not None:
        query = query.filter(Guia.codigo_tercero_fk == guia_codigo_tercero_fk)
    if guia_estado_interface_soporte is not None:
        query = query.filter(Guia.estado_interface_soporte == guia_estado_interface_soporte)
    if fecha_desde_ingreso is not None:
        query = query.filter(Guia.fecha_ingreso >= fecha_desde_ingreso)
    if fecha_hasta_ingreso is not None:
        query = query.filter(Guia.fecha_ingreso < fecha_hasta_ingreso + timedelta(days=1))
    if fecha_desde_despacho is not None:
        query = query.filter(Despacho.fecha_salida >= fecha_desde_despacho)
    if fecha_hasta_despacho is not None:
        query = query.filter(Despacho.fecha_salida < fecha_hasta_despacho + timedelta(days=1))
    if codigo_guia_fk is not None:
        query = query.filter(Seguimiento.codigo_guia_fk == codigo_guia_fk)
    if codigo_seguimiento_tipo_fk is not None:
        query = query.filter(Seguimiento.codigo_seguimiento_tipo_fk == codigo_seguimiento_tipo_fk)
    if codigo_operacion_fk is not None:
        query = query.filter(Seguimiento.codigo_operacion_fk == codigo_operacion_fk)
    if estado_interface is not None:
        query = query.filter(Seguimiento.estado_interface == estado_interface)
    if estado_descartado is not None:
        query = query.filter(Seguimiento.estado_descartado == estado_descartado)
    if fecha_desde is not None:
        query = query.filter(Seguimiento.fecha_seguimiento >= fecha_desde)
    if fecha_hasta is not None:
        # fecha_seguimiento es DateTime: se incluye el día completo de fecha_hasta
        query = query.filter(Seguimiento.fecha_seguimiento < fecha_hasta + timedelta(days=1))
    subconsulta = query.with_entities(Seguimiento.codigo_seguimiento_pk).limit(TOPE_CONTEO_LISTA + 1).subquery()
    conteo = db.query(func.count()).select_from(subconsulta).scalar()
    total_exacto = conteo <= TOPE_CONTEO_LISTA
    total = min(conteo, TOPE_CONTEO_LISTA)
    offset = (page - 1) * size
    if not filtra_guia:
        query = query.outerjoin(Guia, Seguimiento.codigo_guia_fk == Guia.codigo_guia_pk)
    if not filtra_despacho:
        query = query.outerjoin(Despacho, Guia.codigo_despacho_fk == Despacho.codigo_despacho_pk)
    rows = (
        query.add_columns(
            SeguimientoTipo.nombre.label("seguimiento_tipo_nombre"),
            Guia.fecha_ingreso.label("guia_fecha_ingreso"),
            Guia.fecha_ingreso_operacion.label("guia_fecha_ingreso_operacion"),
            Guia.documento_cliente.label("guia_documento_cliente"),
            Guia.documento_cliente_tipo.label("guia_documento_cliente_tipo"),
            Guia.nombre_destinatario.label("guia_nombre_destinatario"),
            Guia.telefono_destinatario.label("guia_telefono_destinatario"),
            Guia.codigo_tercero_operacion_fk.label("guia_codigo_tercero_operacion_fk"),
            Guia.estado_interface_soporte.label("guia_estado_interface_soporte"),
            Despacho.fecha_salida.label("guia_despacho_fecha_salida"),
        )
        .outerjoin(SeguimientoTipo, Seguimiento.codigo_seguimiento_tipo_fk == SeguimientoTipo.codigo_seguimiento_tipo_pk)
        .order_by(Seguimiento.codigo_seguimiento_pk.desc())
        .offset(offset)
        .limit(size)
        .all()
    )
    items = [
        SeguimientoListItemResponse(
            **SeguimientoResponse.model_validate(row.Seguimiento).model_dump(),
            **{campo: valor for campo, valor in row._mapping.items() if campo != "Seguimiento"},
        )
        for row in rows
    ]
    return SeguimientoListResponse(total=total, total_exacto=total_exacto, page=page, size=size, items=items)


@router.get("/detalle/{codigo_seguimiento_pk}", response_model=SeguimientoResponse)
def detalle(codigo_seguimiento_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    seguimiento = db.query(Seguimiento).filter(Seguimiento.codigo_seguimiento_pk == codigo_seguimiento_pk).first()

    if not seguimiento:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")

    return seguimiento


@router.get("/detalle-guia/{codigo_seguimiento_pk}", response_model=SeguimientoDetalleGuiaResponse)
def detalle_guia(codigo_seguimiento_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    seguimiento = (
        db.query(
            Seguimiento.codigo_seguimiento_pk,
            Seguimiento.codigo_seguimiento_tipo_fk,
            Seguimiento.codigo_guia_fk,
            Seguimiento.fecha,
            Seguimiento.fecha_seguimiento,
            Seguimiento.usuario,
            Seguimiento.codigo_operacion_fk,
            Seguimiento.comentario,
            Seguimiento.datos,
            Guia.documento_cliente.label("guia_documento_cliente"),
            Guia.fecha_entrega.label("guia_fecha_entrega"),
            SeguimientoTipo.nombre.label("seguimiento_tipo_nombre"),
            Ciudad.codigo_municipio.label("ciudad_destino_codigo_municipio"),
        )
        .outerjoin(SeguimientoTipo, Seguimiento.codigo_seguimiento_tipo_fk == SeguimientoTipo.codigo_seguimiento_tipo_pk)
        .outerjoin(Guia, Seguimiento.codigo_guia_fk == Guia.codigo_guia_pk)
        .outerjoin(Ciudad, Guia.codigo_ciudad_destino_fk == Ciudad.codigo_ciudad_pk)
        .filter(Seguimiento.codigo_seguimiento_pk == codigo_seguimiento_pk)
        .first()
    )

    if not seguimiento:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")

    return SeguimientoDetalleGuiaResponse(**seguimiento._mapping)


@router.get("/detalle-archivo/{codigo_seguimiento_pk}", response_model=SeguimientoDetalleArchivoResponse)
def detalle_archivo(codigo_seguimiento_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    seguimiento = db.query(Seguimiento).filter(Seguimiento.codigo_seguimiento_pk == codigo_seguimiento_pk).first()

    if not seguimiento:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")

    archivo_base64 = None
    if seguimiento.codigo_guia_fk is not None:
        fichero = (
            db.query(Fichero)
            .filter(Fichero.codigo_modelo_fk == "TteGuia", Fichero.codigo == str(seguimiento.codigo_guia_fk))
            .order_by(Fichero.codigo_fichero_pk.desc())
            .first()
        )
        if fichero:
            directorio = {"F": "firma", "I": "imagen", "G": "fichero"}.get(fichero.codigo_fichero_tipo_fk, "fichero")
            ruta = f"{fichero.directorio_base}/{directorio}/{fichero.codigo_fichero_pk}.{fichero.extension}"
            try:
                contenido, _ = b2_client.download_file(ruta)
            except Exception:
                raise HTTPException(status_code=502, detail="Error al descargar el fichero desde el almacenamiento")
            archivo_base64 = f"data:{fichero.tipo};base64,{base64.b64encode(contenido).decode()}"

    return SeguimientoDetalleArchivoResponse(base64=archivo_base64)


@router.patch("/{codigo_seguimiento_pk}/actualizar-interface", response_model=SeguimientoResponse)
def actualizar_interface(
    codigo_seguimiento_pk: int,
    payload: SeguimientoActualizarInterfaceRequest,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    seguimiento = db.query(Seguimiento).filter(Seguimiento.codigo_seguimiento_pk == codigo_seguimiento_pk).first()

    if not seguimiento:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")

    if payload.actualizar_guia:
        guia = db.query(Guia).filter(Guia.codigo_guia_pk == seguimiento.codigo_guia_fk).first() if seguimiento.codigo_guia_fk is not None else None
        if not guia:
            raise HTTPException(status_code=404, detail="Guía no encontrada")
        guia.estado_interface_soporte = True

    seguimiento.estado_interface = True

    db.commit()
    db.refresh(seguimiento)

    return seguimiento


@router.patch("/{codigo_seguimiento_pk}/descartar", response_model=SeguimientoResponse)
def descartar(codigo_seguimiento_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    seguimiento = db.query(Seguimiento).filter(Seguimiento.codigo_seguimiento_pk == codigo_seguimiento_pk).first()

    if not seguimiento:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")

    seguimiento.estado_descartado = True

    db.commit()
    db.refresh(seguimiento)

    return seguimiento

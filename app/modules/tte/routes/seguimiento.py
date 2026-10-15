import base64
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.core.backblaze import b2_client
from app.core.rate_limit import limiter
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.doc.models.fichero import Fichero
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.guia import Guia
from app.modules.tte.models.operacion import Operacion
from app.modules.tte.models.seguimiento import Seguimiento
from app.modules.tte.models.seguimiento_tipo import SeguimientoTipo
from app.modules.tte.schemas.seguimiento import SeguimientoCreateRequest, SeguimientoResponse, SeguimientoListResponse, SeguimientoDetalleGuiaResponse, SeguimientoDetalleArchivoResponse

router = APIRouter()


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
    page: int = 1,
    size: int = 50,
    codigo_guia_fk: Optional[int] = None,
    codigo_seguimiento_tipo_fk: Optional[str] = None,
    codigo_operacion_fk: Optional[str] = None,
    estado_interface: Optional[bool] = None,
    estado_descartado: Optional[bool] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Seguimiento)
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
    total = query.with_entities(func.count(Seguimiento.codigo_seguimiento_pk)).scalar()
    offset = (page - 1) * size
    seguimientos = query.order_by(Seguimiento.codigo_seguimiento_pk.desc()).offset(offset).limit(size).all()
    return SeguimientoListResponse(total=total, page=page, size=size, items=seguimientos)


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

    return SeguimientoDetalleArchivoResponse(seguimiento=seguimiento, base64=archivo_base64)

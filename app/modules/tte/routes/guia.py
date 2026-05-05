from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.core.config import DEFAULT_EMPRESA_ID
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.empaque import Empaque
from app.modules.tte.models.guia import Guia
from app.modules.tte.models.guia_tipo import GuiaTipo
from app.modules.tte.models.operacion import Operacion
from app.modules.tte.models.producto import Producto
from app.modules.tte.models.servicio import Servicio
from app.modules.tte.schemas.guia import GuiaCreateRequest, GuiaResponse, GuiaEstadoResponse, GuiasMasivoRequest

router = APIRouter()

@router.post("/nuevo", response_model=GuiaCreateRequest)
def nuevo(payload: GuiaCreateRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    fks = [
        (GuiaTipo, GuiaTipo.codigo_guia_tipo_pk, payload.codigo_guia_tipo_fk, "Tipo de guía no encontrado"),
        (Operacion, Operacion.codigo_operacion_pk, payload.codigo_operacion_ingreso_fk, "Operación ingreso no encontrada"),
        (Tercero, Tercero.codigo_tercero_pk, payload.codigo_tercero_fk, "Tercero no encontrado"),
        (Tercero, Tercero.codigo_tercero_pk, payload.codigo_adquiriente_fk, "Adquiriente no encontrado"),
        (Empaque, Empaque.codigo_empaque_pk, payload.codigo_empaque_fk, "Empaque no encontrado"),
        (Producto, Producto.codigo_producto_pk, payload.codigo_producto_fk, "Producto no encontrado"),
        (Servicio, Servicio.codigo_servicio_pk, payload.codigo_servicio_fk, "Servicio no encontrado"),
        (Ciudad, Ciudad.codigo_ciudad_pk, payload.codigo_ciudad_origen_fk, "Ciudad origen no encontrada"),
    ]
    for model, pk_col, value, detail in fks:
        if not db.query(model).filter(pk_col == value).first():
            raise HTTPException(status_code=404, detail=detail)

    ciudad_destino = db.query(Ciudad).filter(Ciudad.codigo_ciudad_pk == payload.codigo_ciudad_destino_fk).first()
    if not ciudad_destino:
        raise HTTPException(status_code=404, detail="Ciudad destino no encontrada")

    tercero = db.query(Tercero).filter(Tercero.codigo_tercero_pk == payload.codigo_tercero_fk).first()

    guia = Guia(
        codigo_guia_tipo_fk=payload.codigo_guia_tipo_fk,
        codigo_operacion_ingreso_fk=payload.codigo_operacion_ingreso_fk,
        codigo_operacion_cargo_fk=payload.codigo_operacion_ingreso_fk,  # Regla de negocio: cargo e ingreso inician con la misma operación; se diferencian en un proceso posterior
        codigo_tercero_fk=payload.codigo_tercero_fk,
        codigo_adquiriente_fk=payload.codigo_adquiriente_fk,
        codigo_empaque_fk=payload.codigo_empaque_fk,
        codigo_producto_fk=payload.codigo_producto_fk,
        codigo_servicio_fk=payload.codigo_servicio_fk,
        codigo_ciudad_origen_fk=payload.codigo_ciudad_origen_fk,
        codigo_ciudad_destino_fk=payload.codigo_ciudad_destino_fk,
        documento_cliente=payload.documento_cliente,
        remitente=payload.remitente,
        nombre_remitente=tercero.nombre_corto,
        direccion_remitente=tercero.direccion,
        telefono_remitente=tercero.telefono,
        codigo_asesor_fk=tercero.codigo_asesor_fk,
        nombre_destinatario=payload.nombre_destinatario,
        direccion_destinatario=payload.direccion_destinatario,
        telefono_destinatario=payload.telefono_destinatario,
        unidades=payload.unidades,
        peso_real=payload.peso_real,
        peso_volumen=payload.peso_volumen,
        peso_facturado=payload.peso_facturado,
        vr_flete=payload.vr_flete,
        vr_manejo=payload.vr_manejo,
        vr_declara=payload.vr_declara,
        codigo_empresa_fk=DEFAULT_EMPRESA_ID,
        codigo_ruta_fk=ciudad_destino.codigo_ruta_fk,
        latitud=float(ciudad_destino.latitud) if ciudad_destino.latitud else None,
        longitud=float(ciudad_destino.longitud) if ciudad_destino.longitud else None,
        fecha_ingreso=datetime.now(),
        fecha_recogido=datetime.now(),
        fecha_ingreso_operacion=datetime.now(),
        estado_recogido=payload.estado_recogido,
        estado_ingreso=payload.estado_ingreso,
        ui="API2",
        estado_impreso=True,
        estado_aprobado=True,
        estado_autorizado=True,
    )

    db.add(guia)
    db.commit()
    db.refresh(guia)

    return guia

@router.get("/lista", response_model=List[GuiaResponse])
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    offset = (page - 1) * size
    guias = (
        db.query(Guia)
        .offset(offset)
        .limit(size)
        .all()
    )

    return guias

@router.get("/estado/{guia}", response_model=GuiaEstadoResponse)
def estado(guia: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    guia = db.query(Guia).filter(Guia.codigo_guia_pk == guia).first()

    if not guia:
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    return guia

@router.post("/estado-masivo", response_model=List[GuiaEstadoResponse])
def estado_masivo(payload: GuiasMasivoRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    resultados = db.query(Guia).filter(Guia.codigo_guia_pk.in_(payload.guias)).all()

    if not resultados:
        raise HTTPException(status_code=404, detail="Ninguna guía encontrada")

    return resultados

@router.get("/estado-documento/{codigo_tercero}/{documento_cliente}", response_model=GuiaEstadoResponse)
def estado_documento(codigo_tercero: int, documento_cliente: str, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):

    stmt = (
        select(Guia)
        .where(
            Guia.codigo_tercero_fk == codigo_tercero,
            Guia.documento_cliente == documento_cliente
        )
        .limit(1)
    )

    guia = db.execute(stmt).scalar_one_or_none()

    if guia is None:
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    return guia
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
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
from app.modules.tte.schemas.guia import GuiaCreateRequest, GuiaCreateResponse, GuiaCorreccionRequest, GuiaCorreccionResponse, GuiaListResponse, GuiaEstadoResponse, GuiasMasivoRequest, LiquidarRequest, LiquidarResponse
from app.modules.tte.services import guia as guia_service

router = APIRouter()

@router.post("/nuevo", response_model=GuiaCreateResponse)
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
    cobro_entrega = 0
    if payload.vr_recaudo > 0:
        cobro_entrega = payload.vr_recaudo

    vr_flete = payload.vr_flete
    vr_manejo = payload.vr_manejo
    peso_facturado = payload.peso_facturado
    if payload.liquidar:
        resultado = guia_service.liquidar(
            db,
            tercero=payload.codigo_tercero_fk,
            condicion_id=payload.condicion,
            precio=payload.precio,
            origen=payload.codigo_ciudad_origen_fk,
            destino=payload.codigo_ciudad_destino_fk,
            producto=payload.codigo_producto_fk,
            zona=payload.zona,
            tipo_liquidacion=payload.tipo_liquidacion,
            unidades=payload.unidades,
            peso=payload.peso_real,
            volumen=payload.peso_volumen,
            declarado=payload.vr_declara,
        )
        vr_flete = resultado["flete"]
        vr_manejo = resultado["manejo"]
        peso_facturado = resultado["peso_facturado"]

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
        peso_facturado=peso_facturado,
        vr_flete=vr_flete,
        vr_manejo=vr_manejo,
        vr_declara=payload.vr_declara,
        vr_recaudo=payload.vr_recaudo,
        vr_cobro_entrega=cobro_entrega,
        tipo_liquidacion=payload.tipo_liquidacion,
        codigo_empresa_fk=DEFAULT_EMPRESA_ID,
        codigo_ruta_fk=ciudad_destino.codigo_ruta_fk,
        latitud=float(ciudad_destino.latitud) if ciudad_destino.latitud else None,
        longitud=float(ciudad_destino.longitud) if ciudad_destino.longitud else None,
        fecha_ingreso=datetime.now(),
        fecha_recogido=datetime.now(),
        fecha_ingreso_operacion=datetime.now(),
        estado_recogido=payload.estado_recogido,
        estado_ingreso=payload.estado_ingreso,
        devolver_documento_cliente=payload.devolver_documento_cliente,
        comentario=payload.comentario,
        ui="API_F",
        estado_impreso=True,
        estado_aprobado=True,
        estado_autorizado=True,
    )

    db.add(guia)
    db.commit()
    db.refresh(guia)

    return guia

@router.get("/lista", response_model=GuiaListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    tercero_id: Optional[int] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    estado_ingreso: Optional[bool] = None,
    estado_despachado: Optional[bool] = None,
    estado_entregado: Optional[bool] = None,
    estado_novedad: Optional[bool] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Guia)
    if tercero_id is not None:
        query = query.filter(Guia.codigo_tercero_fk == tercero_id)
    if fecha_desde is not None:
        query = query.filter(Guia.fecha_ingreso >= fecha_desde)
    if fecha_hasta is not None:
        query = query.filter(Guia.fecha_ingreso <= fecha_hasta)
    if estado_ingreso is not None:
        query = query.filter(Guia.estado_ingreso == estado_ingreso)
    if estado_despachado is not None:
        query = query.filter(Guia.estado_despachado == estado_despachado)
    if estado_entregado is not None:
        query = query.filter(Guia.estado_entregado == estado_entregado)
    if estado_novedad is not None:
        query = query.filter(Guia.estado_novedad == estado_novedad)
    total = query.with_entities(func.count(Guia.codigo_guia_pk)).scalar()
    offset = (page - 1) * size
    guias = query.order_by(Guia.codigo_guia_pk.desc()).offset(offset).limit(size).all()
    return GuiaListResponse(total=total, page=page, size=size, items=guias)

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

@router.get("/imprimir-rotulo")
def imprimir_rotulo(
    numero_desde: int,
    numero_hasta: int,
    formato: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    if numero_desde > numero_hasta:
        raise HTTPException(status_code=400, detail="numero_desde no puede ser mayor que numero_hasta")

    guias = (
        db.query(Guia)
        .options(
            joinedload(Guia.ciudad_origen),
            joinedload(Guia.ciudad_destino),
            joinedload(Guia.tercero),
            joinedload(Guia.empaque),
            joinedload(Guia.servicio),
            joinedload(Guia.producto),
            joinedload(Guia.guia_tipo),
        )
        .filter(Guia.codigo_guia_pk >= numero_desde, Guia.codigo_guia_pk <= numero_hasta)
        .order_by(Guia.codigo_guia_pk)
        .limit(31)
        .all()
    )

    if not guias:
        raise HTTPException(status_code=404, detail="No se encontraron guías en el rango indicado")

    if len(guias) > 30:
        raise HTTPException(status_code=400, detail="El rango contiene más de 30 guías. Ajuste numero_desde y numero_hasta")

    # --- Impresión masiva de rótulos ---
    from app.modules.tte.formats.rotulo_pdf import generar
    try:
        pdf_bytes = generar(guias, formato=formato, db=db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=rotulos_{numero_desde}_{numero_hasta}.pdf"},
    )

@router.get("/imprimir-guia")
def imprimir_guia(
    numero_desde: int,
    numero_hasta: int,
    formato: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    if numero_desde > numero_hasta:
        raise HTTPException(status_code=400, detail="numero_desde no puede ser mayor que numero_hasta")

    guias = (
        db.query(Guia)
        .options(
            joinedload(Guia.ciudad_origen),
            joinedload(Guia.ciudad_destino),
            joinedload(Guia.tercero),
            joinedload(Guia.adquiriente),
            joinedload(Guia.empaque),
            joinedload(Guia.servicio),
            joinedload(Guia.producto),
            joinedload(Guia.guia_tipo),
            joinedload(Guia.operacion_ingreso),
        )
        .filter(Guia.codigo_guia_pk >= numero_desde, Guia.codigo_guia_pk <= numero_hasta)
        .order_by(Guia.codigo_guia_pk)
        .limit(31)
        .all()
    )

    if not guias:
        raise HTTPException(status_code=404, detail="No se encontraron guías en el rango indicado")

    if len(guias) > 30:
        raise HTTPException(status_code=400, detail="El rango contiene más de 30 guías. Ajuste numero_desde y numero_hasta")

    from app.modules.tte.formats.guia_pdf import generar
    try:
        pdf_bytes = generar(guias, formato=formato, db=db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=guias_{numero_desde}_{numero_hasta}.pdf"},
    )

@router.patch("/corregir/{codigo_guia_pk}", response_model=GuiaCorreccionResponse)
def corregir(codigo_guia_pk: int, payload: GuiaCorreccionRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    guia = db.query(Guia).filter(Guia.codigo_guia_pk == codigo_guia_pk).first()

    if not guia:
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    guia.unidades = payload.unidades
    guia.peso_real = payload.peso_real
    guia.peso_volumen = payload.peso_volumen
    guia.peso_facturado = payload.peso_facturado
    guia.correccion = True

    db.commit()
    db.refresh(guia)

    return guia

@router.post("/liquidar", response_model=LiquidarResponse)
def liquidar(payload: LiquidarRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    resultado = guia_service.liquidar(
        db,
        tercero=payload.tercero,
        condicion_id=payload.condicion,
        precio=payload.precio,
        origen=payload.origen,
        destino=payload.destino,
        producto=payload.producto,
        zona=payload.zona,
        tipo_liquidacion=payload.tipo_liquidacion,
        unidades=payload.unidades,
        peso=payload.peso,
        volumen=payload.volumen,
        declarado=payload.declarado,
    )
    return LiquidarResponse(**resultado)
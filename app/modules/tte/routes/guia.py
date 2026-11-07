import logging
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from typing import Literal, Optional
from app.core.tenant_database import get_tenant_db
from app.core.master_database import get_master_db
from app.core.security import get_current_user
from app.core.config import DEFAULT_EMPRESA_ID
from app.core.rate_limit import limiter
from app.core.utils import Filtro, ListaConfig, exportar_excel, paginar
from app.modules.gen.models.asesor import Asesor
from app.modules.gen.models.identificacion import Identificacion
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.cierre import Cierre
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.condicion import Condicion
from app.modules.tte.models.destinatario import Destinatario
from app.modules.tte.models.empaque import Empaque
from app.modules.tte.models.guia import Guia
from app.modules.tte.models.guia_tipo import GuiaTipo
from app.modules.tte.models.operacion import Operacion
from app.modules.tte.models.producto import Producto
from app.modules.tte.models.ruta import Ruta
from app.modules.tte.models.seguimiento import Seguimiento
from app.modules.tte.models.servicio import Servicio
from app.modules.tte.models.tercero_operacion import TerceroOperacion
from app.modules.tte.models.zona import Zona
from app.modules.tte.schemas.guia import GuiaFormatoImpresionResponse, GuiaCreateRequest, GuiaDetalleResponse, GuiaCreateResponse, GuiaCorreccionRequest, GuiaCorreccionResponse, GuiaListResponse, GuiaEstadoResponse, GuiaRecogidoRequest, GuiaRecogidoResponse, GuiaIngresoRequest, GuiaIngresoResponse, GuiaEntregaRequest, GuiaEntregaResponse, GuiasMasivoRequest, GuiasDocumentoMasivoRequest, LiquidarRequest, LiquidarResponse, CondicionEspecialRequest, CondicionEspecialResponse, ReliquidarRequest, ReliquidarResponse
from app.modules.tte.services import guia as guia_service
from app.modules.tte.formats import guia as formatos_guia, rotulo as formatos_rotulo
from app.modules.tte.formats.datos import MAXIMO_GUIAS, cargar_empresa, cargar_guias, preparar_guias

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/nuevo", response_model=GuiaCreateResponse)
def nuevo(payload: GuiaCreateRequest, db: Session = Depends(get_tenant_db), master_db: Session = Depends(get_master_db), current_user: dict = Depends(get_current_user)):
    fks = [
        (Operacion, Operacion.codigo_operacion_pk, payload.codigo_operacion_ingreso_fk, "Operación ingreso no encontrada"),
        (Tercero, Tercero.codigo_tercero_pk, payload.codigo_tercero_fk, "Tercero no encontrado"),
        (Tercero, Tercero.codigo_tercero_pk, payload.codigo_adquiriente_fk, "Adquiriente no encontrado"),
        (Empaque, Empaque.codigo_empaque_pk, payload.codigo_empaque_fk, "Empaque no encontrado"),
        (Producto, Producto.codigo_producto_pk, payload.codigo_producto_fk, "Producto no encontrado"),
        (Servicio, Servicio.codigo_servicio_pk, payload.codigo_servicio_fk, "Servicio no encontrado"),
        (Ciudad, Ciudad.codigo_ciudad_pk, payload.codigo_ciudad_origen_fk, "Ciudad origen no encontrada"),
    ]
    # FKs opcionales: se validan solo si llegan
    fks_opcionales = [
        (Operacion, Operacion.codigo_operacion_pk, payload.codigo_operacion_cargo_fk, "Operación cargo no encontrada"),
        (Identificacion, Identificacion.codigo_identificacion_pk, payload.codigo_identificacion_destinatario_fk, "Identificación del destinatario no encontrada"),
        (Destinatario, Destinatario.codigo_destinatario_pk, payload.codigo_destinatario_fk, f"Destinatario {payload.codigo_destinatario_fk} no encontrado"),
        (Ruta, Ruta.codigo_ruta_pk, payload.codigo_ruta_fk, "Ruta no encontrada"),
        (Asesor, Asesor.codigo_asesor_pk, payload.codigo_asesor_fk, "Asesor no encontrado"),
        (Zona, Zona.codigo_zona_pk, payload.zona, "Zona no encontrada"),
        (Condicion, Condicion.codigo_condicion_pk, payload.condicion, "Condición no encontrada"),
    ]
    fks += [fk for fk in fks_opcionales if fk[2] is not None]
    for model, pk_col, value, detail in fks:
        if not db.query(model).filter(pk_col == value).first():
            raise HTTPException(status_code=404, detail=detail)

    guia_tipo = db.query(GuiaTipo).filter(GuiaTipo.codigo_guia_tipo_pk == payload.codigo_guia_tipo_fk).first()
    if not guia_tipo:
        raise HTTPException(status_code=404, detail="Tipo de guía no encontrado")

    ciudad_destino = db.query(Ciudad).filter(Ciudad.codigo_ciudad_pk == payload.codigo_ciudad_destino_fk).first()
    if not ciudad_destino:
        raise HTTPException(status_code=404, detail="Ciudad destino no encontrada")

    if payload.codigo_tercero_operacion_fk is not None:
        tercero_operacion = db.query(TerceroOperacion).filter(TerceroOperacion.codigo_tercero_operacion_pk == payload.codigo_tercero_operacion_fk).first()
        if not tercero_operacion or tercero_operacion.codigo_tercero_fk != payload.codigo_tercero_fk:
            raise HTTPException(status_code=404, detail="Tercero operación no encontrado")

    tercero = db.query(Tercero).filter(Tercero.codigo_tercero_pk == payload.codigo_tercero_fk).first()
    vr_flete = payload.vr_flete or 0
    vr_manejo = payload.vr_manejo or 0
    vr_recaudo = payload.vr_recaudo or 0

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
            pago=guia_tipo.codigo_pago_fk,
        )
        vr_flete = resultado["flete"]
        vr_manejo = resultado["manejo"]
        peso_facturado = resultado["peso_facturado"]

    if guia_tipo.cortesia:
        vr_flete = 0
        vr_manejo = 0

    cobro_entrega = vr_recaudo
    if guia_tipo.genera_cobro:
        cobro_entrega += vr_flete + vr_manejo

    guia = Guia(
        codigo_guia_tipo_fk=payload.codigo_guia_tipo_fk,
        codigo_operacion_ingreso_fk=payload.codigo_operacion_ingreso_fk,
        # Regla de negocio: si no llega, cargo inicia igual a ingreso; se diferencian en un proceso posterior
        codigo_operacion_cargo_fk=payload.codigo_operacion_cargo_fk or payload.codigo_operacion_ingreso_fk,
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
        direccion_remitente=payload.direccion_remitente if payload.direccion_remitente is not None else tercero.direccion,
        telefono_remitente=payload.telefono_remitente if payload.telefono_remitente is not None else tercero.telefono,
        codigo_asesor_fk=payload.codigo_asesor_fk if payload.codigo_asesor_fk is not None else tercero.codigo_asesor_fk,
        relacion_cliente=payload.relacion_cliente,
        codigo_destinatario_fk=payload.codigo_destinatario_fk,
        codigo_identificacion_destinatario_fk=payload.codigo_identificacion_destinatario_fk,
        numero_identificacion_destinatario=payload.numero_identificacion_destinatario,
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
        vr_recaudo=vr_recaudo,
        vr_cobro_entrega=cobro_entrega,
        vr_otros=payload.vr_otros,
        tipo_liquidacion=payload.tipo_liquidacion,
        codigo_empresa_fk=DEFAULT_EMPRESA_ID,
        codigo_ruta_fk=payload.codigo_ruta_fk or ciudad_destino.codigo_ruta_fk,
        codigo_zona_fk=payload.zona or ciudad_destino.codigo_zona_fk,
        codigo_condicion_fk=payload.condicion,
        orden_ruta=payload.orden_ruta if payload.orden_ruta is not None else 0,
        latitud=float(ciudad_destino.latitud) if ciudad_destino.latitud else None,
        longitud=float(ciudad_destino.longitud) if ciudad_destino.longitud else None,
        fecha_ingreso=datetime.now(),
        usuario=payload.usuario or guia_service.usuario_autenticado(master_db, current_user),
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
        codigo_tercero_operacion_fk=payload.codigo_tercero_operacion_fk,
        documento_cliente_tipo=payload.documento_cliente_tipo,
        empaque_referencia=payload.empaque_referencia,
        mercancia_peligrosa=payload.mercancia_peligrosa,
        contenido_verificado=payload.contenido_verificado,
        cortesia=bool(guia_tipo.cortesia),
        factura=bool(guia_tipo.factura),
        codigo_pago_fk=guia_tipo.codigo_pago_fk,
        reexpedicion=bool(ciudad_destino.reexpedicion),
    )

    db.add(guia)
    db.commit()
    db.refresh(guia)

    return guia

LISTA_GUIA = ListaConfig(
    pk=Guia.codigo_guia_pk,
    orden=[Guia.codigo_guia_pk.desc()],
    filtros={
        "codigo_guia_pk": Filtro(Guia.codigo_guia_pk),
        "codigo_tercero_fk": Filtro(Guia.codigo_tercero_fk),
        "documento_cliente": Filtro(Guia.documento_cliente),
        "codigo_guia_tipo_fk": Filtro(Guia.codigo_guia_tipo_fk),
        "codigo_servicio_fk": Filtro(Guia.codigo_servicio_fk),
        "codigo_ciudad_origen_fk": Filtro(Guia.codigo_ciudad_origen_fk),
        "codigo_ciudad_destino_fk": Filtro(Guia.codigo_ciudad_destino_fk),
        "codigo_despacho_fk": Filtro(Guia.codigo_despacho_fk),
        "codigo_tercero_operacion_fk": Filtro(Guia.codigo_tercero_operacion_fk),
        "fecha_desde": Filtro(Guia.fecha_ingreso, "gte", tipo=date, descripcion="Fecha de ingreso desde"),
        "fecha_hasta": Filtro(Guia.fecha_ingreso, "hasta_dia", tipo=date, descripcion="Fecha de ingreso hasta (incluye el día)"),
        "estado_ingreso": Filtro(Guia.estado_ingreso),
        "estado_despachado": Filtro(Guia.estado_despachado),
        "estado_entregado": Filtro(Guia.estado_entregado),
        "estado_novedad": Filtro(Guia.estado_novedad),
        "estado_anulado": Filtro(Guia.estado_anulado),
    },
    ordenables={
        "codigo_guia_pk": Guia.codigo_guia_pk,
        "fecha_ingreso": Guia.fecha_ingreso,
        "documento_cliente": Guia.documento_cliente,
    },
    # La lista no muestra nombres de relaciones; el Excel sí
    relaciones_excel=[Guia.guia_tipo, Guia.tercero, Guia.ciudad_origen, Guia.ciudad_destino, Guia.servicio],
    columnas_excel=[
        ("Guía", "codigo_guia_pk"),
        ("Tipo", "guia_tipo_nombre"),
        ("Fecha ingreso", "fecha_ingreso"),
        ("Documento cliente", "documento_cliente"),
        ("Cliente", "tercero_nombre"),
        ("Remitente", "remitente"),
        ("Destinatario", "nombre_destinatario"),
        ("Dirección destinatario", "direccion_destinatario"),
        ("Teléfono destinatario", "telefono_destinatario"),
        ("Origen", "ciudad_origen_nombre"),
        ("Destino", "ciudad_destino_nombre"),
        ("Servicio", "servicio_nombre"),
        ("Despacho", "codigo_despacho_fk"),
        ("Unidades", "unidades"),
        ("Peso real", "peso_real"),
        ("Peso volumen", "peso_volumen"),
        ("Peso facturado", "peso_facturado"),
        ("Vr declarado", "vr_declara"),
        ("Vr flete", "vr_flete"),
        ("Vr manejo", "vr_manejo"),
        ("Vr recaudo", "vr_recaudo"),
        ("Ingreso", "estado_ingreso"),
        ("Despachado", "estado_despachado"),
        ("Fecha despacho", "fecha_despacho"),
        ("Entregado", "estado_entregado"),
        ("Fecha entrega", "fecha_entrega"),
        ("Cumplido", "estado_cumplido"),
        ("Novedad", "estado_novedad"),
        ("Anulado", "estado_anulado"),
    ],
)


@router.get("/lista", response_model=GuiaListResponse)
def lista(params: dict = Depends(LISTA_GUIA.params_lista), db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    return paginar(db, LISTA_GUIA, params)


@router.get("/excel")
@limiter.limit("5/minute")
def excel(request: Request, response: Response, params: dict = Depends(LISTA_GUIA.params_excel), db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    return exportar_excel(db, LISTA_GUIA, params, nombre="guias")


@router.get("/detalle/{codigo_guia_pk}", response_model=GuiaDetalleResponse)
def detalle(codigo_guia_pk: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    guia = (
        db.query(Guia)
        .options(
            joinedload(Guia.tercero),
            joinedload(Guia.adquiriente),
            joinedload(Guia.asesor),
            joinedload(Guia.guia_tipo),
            joinedload(Guia.producto),
            joinedload(Guia.empaque),
            joinedload(Guia.servicio),
            joinedload(Guia.operacion_ingreso),
            joinedload(Guia.operacion_cargo),
            joinedload(Guia.ciudad_origen),
            joinedload(Guia.ciudad_destino),
            joinedload(Guia.condicion),
        )
        .filter(Guia.codigo_guia_pk == codigo_guia_pk)
        .first()
    )

    if not guia:
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    return guia

@router.get("/estado/{guia}", response_model=GuiaEstadoResponse)
def estado(guia: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    guia = db.query(Guia).filter(Guia.codigo_guia_pk == guia).first()

    if not guia:
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    return guia

@router.post("/estado-masivo", response_model=list[GuiaEstadoResponse])
def estado_masivo(payload: GuiasMasivoRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    resultados = db.query(Guia).filter(Guia.codigo_guia_pk.in_(payload.guias)).all()

    if not resultados:
        raise HTTPException(status_code=404, detail="Ninguna guía encontrada")

    return resultados

@router.get("/estado-por-fecha", response_model=list[GuiaEstadoResponse])
def estado_por_fecha(
    fecha_desde: date,
    fecha_hasta: date,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    if fecha_hasta < fecha_desde:
        raise HTTPException(status_code=400, detail="fecha_hasta debe ser mayor o igual a fecha_desde")

    stmt = (
        select(Guia)
        .where(
            Guia.fecha_ingreso >= fecha_desde,
            Guia.fecha_ingreso < fecha_hasta + timedelta(days=1),
        )
        .order_by(Guia.fecha_ingreso)
        .limit(1000)
    )
    resultados = db.execute(stmt).scalars().all()

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

@router.post("/estado-documento-masivo", response_model=list[GuiaEstadoResponse])
def estado_documento_masivo(payload: GuiasDocumentoMasivoRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    stmt = (
        select(Guia)
        .where(
            Guia.codigo_tercero_fk == payload.codigo_tercero,
            Guia.documento_cliente.in_(payload.documentos)
        )
        .order_by(Guia.codigo_guia_pk)
    )
    resultados = db.execute(stmt).scalars().all()

    if not resultados:
        raise HTTPException(status_code=404, detail="Ninguna guía encontrada")

    return resultados

_IMPRESIONES = {"guia": formatos_guia, "rotulo": formatos_rotulo}


@router.get("/formatos-impresion", response_model=list[GuiaFormatoImpresionResponse])
def formatos_impresion(
    tipo: Literal["guia", "rotulo"] = "guia",
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    formatos = _IMPRESIONES[tipo]
    predeterminado = formatos.resolver_formato(None, cargar_empresa(db))
    return [
        GuiaFormatoImpresionResponse(codigo=f.codigo, nombre=f.nombre, predeterminado=f.codigo == predeterminado)
        for f in formatos.registro.listar()
    ]


# Las impresiones devuelven el PDF en bruto, no JSON; esto lo declara así en OpenAPI.
_RESPUESTA_PDF = {
    200: {
        "description": "Archivo PDF",
        "content": {"application/pdf": {"schema": {"type": "string", "format": "binary"}}},
    }
}


@router.get(
    "/imprimir-guia",
    response_class=Response,
    responses=_RESPUESTA_PDF,
    description=(
        f"PDF de las guías no anuladas del rango (máximo {MAXIMO_GUIAS}). Si no se envía `formato`, se usa "
        "`codigo_formato_guia_web` de la configuración y, si no hay uno válido, el formato 3."
    ),
)
def imprimir_guia(
    numero_desde: int,
    numero_hasta: int,
    formato: Optional[int] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    return _imprimir(db, formatos_guia, numero_desde, numero_hasta, formato, "guias")


@router.get(
    "/imprimir-rotulo",
    response_class=Response,
    responses=_RESPUESTA_PDF,
    description=(
        f"PDF con un rótulo por unidad de las guías no anuladas del rango (máximo {MAXIMO_GUIAS} guías). Si no se "
        "envía `formato`, se usa `codigo_formato_rotulo` de la configuración y, si no hay uno válido, el 1."
    ),
)
def imprimir_rotulo(
    numero_desde: int,
    numero_hasta: int,
    formato: Optional[int] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    return _imprimir(db, formatos_rotulo, numero_desde, numero_hasta, formato, "rotulos")


def _imprimir(db: Session, formatos, numero_desde: int, numero_hasta: int, formato: Optional[int], nombre: str) -> Response:
    """Valida el rango, elige el formato y genera el PDF (común a guías y rótulos)."""
    if numero_desde > numero_hasta:
        raise HTTPException(status_code=400, detail="numero_desde no puede ser mayor que numero_hasta")

    empresa = cargar_empresa(db)
    try:
        codigo_formato = formatos.resolver_formato(formato, empresa)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    guias = cargar_guias(db, numero_desde, numero_hasta)
    if not guias:
        raise HTTPException(status_code=404, detail="No se encontraron guías en el rango indicado")
    if len(guias) > MAXIMO_GUIAS:
        raise HTTPException(status_code=400, detail=f"El rango contiene más de {MAXIMO_GUIAS} guías. Ajuste numero_desde y numero_hasta")

    usa_firma = getattr(formatos.registro.obtener(codigo_formato), "usa_firma", False)
    documentos = preparar_guias(db, guias, empresa, con_firma=usa_firma)
    pdf_bytes = formatos.registro.generar(codigo_formato, documentos, empresa)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={nombre}_{numero_desde}_{numero_hasta}.pdf"},
    )

@router.patch("/corregir/{codigo_guia_pk}", response_model=GuiaCorreccionResponse)
def corregir(codigo_guia_pk: int, payload: GuiaCorreccionRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    guia = db.query(Guia).filter(Guia.codigo_guia_pk == codigo_guia_pk).first()
    if not guia:
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    if guia.estado_facturado:
        raise HTTPException(status_code=409, detail="La guía se encuentra facturada, no se puede editar")

    if not guia.fecha_ingreso:
        raise HTTPException(status_code=409, detail="La guía no tiene fecha de ingreso, no se puede validar el periodo de cierre")

    anio = guia.fecha_ingreso.year
    mes = guia.fecha_ingreso.month
    cierre = db.query(Cierre).filter(Cierre.anio == anio, Cierre.mes == mes).first()
    if not cierre:
        raise HTTPException(status_code=409, detail=f"No existe el periodo de cierre {anio} {mes}")
    if cierre.estado_autorizado:
        raise HTTPException(status_code=409, detail=f"El cierre {anio} {mes} ya esta autorizado y no se puede editar la guía")

    cambios = payload.model_dump(exclude_unset=True, exclude_none=True)

    codigo_ciudad_destino = cambios.pop("codigo_ciudad_destino_fk", None)
    if codigo_ciudad_destino is not None:
        ciudad_destino = db.query(Ciudad).filter(Ciudad.codigo_ciudad_pk == codigo_ciudad_destino).first()
        if not ciudad_destino:
            raise HTTPException(status_code=404, detail="La ciudad destino ingresada no existe, por favor validar")
        guia.codigo_ciudad_destino_fk = ciudad_destino.codigo_ciudad_pk

    for campo, valor in cambios.items():
        setattr(guia, campo, valor)

    if guia.cortesia:
        guia.vr_flete = 0
        guia.vr_manejo = 0

    cobro_entrega = guia.vr_recaudo or 0
    if guia.guia_tipo and guia.guia_tipo.genera_cobro:
        cobro_entrega += (guia.vr_flete or 0) + (guia.vr_manejo or 0)
    guia.vr_cobro_entrega = cobro_entrega
    guia.correccion = True

    db.commit()
    db.refresh(guia)

    return guia

@router.post("/recogido", response_model=GuiaRecogidoResponse)
def recogido(payload: GuiaRecogidoRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    guia = db.query(Guia).filter(Guia.codigo_guia_pk == payload.guia).first()

    if not guia:
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    if guia.estado_recogido:
        raise HTTPException(status_code=409, detail="La guía ya se encuentra recogida")

    ahora = datetime.now()
    guia.estado_recogido = True
    guia.fecha_recogido = ahora

    seguimiento = Seguimiento(
        codigo_guia_fk=guia.codigo_guia_pk,
        codigo_seguimiento_tipo_fk="RECOGIDO",
        fecha=ahora,
        fecha_seguimiento=ahora,
        usuario=current_user["sub"],
        comentario="CAPA API-KEY",
    )
    db.add(seguimiento)

    db.commit()
    db.refresh(guia)

    return guia

@router.post("/ingreso", response_model=GuiaIngresoResponse)
def ingreso(payload: GuiaIngresoRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    guia = db.query(Guia).filter(Guia.codigo_guia_pk == payload.guia).first()

    if not guia:
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    if not guia.estado_recogido:
        raise HTTPException(status_code=409, detail="La guía no ha sido recogida")

    if guia.estado_ingreso:
        raise HTTPException(status_code=409, detail="La guía ya tiene ingreso")

    ahora = datetime.now()
    guia.estado_ingreso = True
    guia.fecha_ingreso_operacion = ahora

    seguimiento = Seguimiento(
        codigo_guia_fk=guia.codigo_guia_pk,
        codigo_seguimiento_tipo_fk="INGRESO",
        fecha=ahora,
        fecha_seguimiento=ahora,
        usuario=current_user["sub"],
        comentario="CAPA API-KEY",
    )
    db.add(seguimiento)

    db.commit()
    db.refresh(guia)

    return guia

@router.post("/entrega", response_model=GuiaEntregaResponse)
def entrega(
    datos: str = Form(..., description="JSON con los datos de la entrega (GuiaEntregaRequest)"),
    imagenes: list[UploadFile] = File(default=[], description="Fotos de la entrega, JPEG, PNG o WebP"),
    firma: Optional[UploadFile] = File(default=None, description="Firma de quien recibe, PNG"),
    db: Session = Depends(get_tenant_db),
    master_db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    payload = guia_service.parsear_datos_entrega(datos)
    archivos_imagenes, archivo_firma = guia_service.leer_archivos_entrega(imagenes, firma)
    usuario = payload.usuario or guia_service.usuario_autenticado(master_db, current_user)
    return guia_service.registrar_entrega(db, payload, archivos_imagenes, archivo_firma, usuario)


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

@router.post(
    "/condicion-especial",
    response_model=CondicionEspecialResponse,
    description="Precio y condiciones especiales (flete y manejo) que aplican al tercero para un origen/destino (replica condicionEspecial de PHP).",
)
def condicion_especial(payload: CondicionEspecialRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    resultado = guia_service.condicion_especial(
        db,
        tercero=payload.codigo_tercero,
        origen=payload.origen,
        destino=payload.destino,
        precio=payload.precio,
        guia_tipo=payload.guia_tipo,
        producto=payload.producto,
    )
    if resultado is None:
        raise HTTPException(status_code=404, detail="Tercero no encontrado")
    return CondicionEspecialResponse(**resultado)

@router.post("/reliquidar", response_model=ReliquidarResponse)
def reliquidar(payload: ReliquidarRequest, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    guia = db.query(Guia).filter(Guia.codigo_guia_pk == payload.codigo_guia_pk).first()
    if not guia:
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    if guia.estado_facturado:
        raise HTTPException(status_code=409, detail="La guía se encuentra facturada, no se puede reliquidar")

    if not guia.fecha_ingreso:
        raise HTTPException(status_code=409, detail="La guía no tiene fecha de ingreso, no se puede validar el periodo de cierre")

    anio = guia.fecha_ingreso.year
    mes = guia.fecha_ingreso.month
    cierre = db.query(Cierre).filter(Cierre.anio == anio, Cierre.mes == mes).first()
    if not cierre:
        raise HTTPException(status_code=409, detail=f"No existe el periodo de cierre {anio} {mes}")
    if cierre.estado_autorizado:
        raise HTTPException(status_code=409, detail=f"El cierre {anio} {mes} ya esta autorizado y no se puede reliquidar la guía")

    tipo_liquidacion = payload.tipo_liquidacion or guia.tipo_liquidacion or "K"
    tercero = guia.tercero
    # La reliquidación usa la condición actual del tercero y la deja guardada en la guía
    condicion_id = tercero.codigo_condicion_fk if tercero else None
    resultado = guia_service.liquidar(
        db,
        tercero=guia.codigo_tercero_fk,
        condicion_id=condicion_id,
        precio=tercero.condicion_codigo_precio_fk if tercero else None,
        origen=guia.codigo_ciudad_origen_fk,
        destino=guia.codigo_ciudad_destino_fk,
        producto=guia.codigo_producto_fk,
        zona=payload.zona or guia.codigo_zona_fk,
        tipo_liquidacion=tipo_liquidacion,
        unidades=guia.unidades,
        peso=guia.peso_real,
        volumen=guia.peso_volumen,
        declarado=guia.vr_declara,
        pago=guia.guia_tipo.codigo_pago_fk if guia.guia_tipo else None,
    )

    guia.tipo_liquidacion = tipo_liquidacion
    guia.codigo_condicion_fk = condicion_id
    guia.peso_facturado = resultado["peso_facturado"]
    guia.vr_flete = resultado["flete"]
    guia.vr_manejo = resultado["manejo"]
    guia.correccion = True

    db.commit()
    db.refresh(guia)

    return guia

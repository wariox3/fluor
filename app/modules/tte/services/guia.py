import json
import logging
import random
from datetime import datetime

import magic
from fastapi import HTTPException, UploadFile
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.backblaze import b2_client
from app.core.utils import comprimir_imagen
from app.modules.auth.models.api_key import ApiKey
from app.modules.auth.models.user import User
from app.modules.doc.models.fichero import Fichero
from app.modules.gen.models.configuracion import Configuracion
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.condicion import Condicion
from app.modules.tte.models.condicion_flete import CondicionFlete
from app.modules.tte.models.condicion_manejo import CondicionManejo
from app.modules.tte.models.guia_tipo import GuiaTipo
from app.modules.tte.models.despacho import Despacho
from app.modules.tte.models.guia import Guia
from app.modules.tte.models.precio_detalle import PrecioDetalle
from app.modules.tte.models.seguimiento import Seguimiento
from app.modules.tte.models.ubicacion import Ubicacion
from app.modules.tte.schemas.guia import GuiaEntregaRequest, GuiaEntregaResponse

logger = logging.getLogger(__name__)


def _buscar_precio_detalle(db: Session, precio, origen, destino, producto, zona):
    """Replica TtePrecioDetalleRepository::apiWindowsDetalleProducto."""
    if not (precio and origen and destino and producto):
        return None
    base = db.query(PrecioDetalle).filter(
        PrecioDetalle.codigo_precio_fk == precio,
        PrecioDetalle.codigo_ciudad_origen_fk == origen,
        PrecioDetalle.codigo_producto_fk == producto,
    )
    # 1) origen + destino
    detalle = base.filter(PrecioDetalle.codigo_ciudad_destino_fk == destino).first()
    if detalle:
        return detalle
    # 2) origen + zona
    if zona:
        detalle = base.filter(PrecioDetalle.codigo_zona_fk == zona).first()
        if detalle:
            return detalle
    # 3) origen + zona NULL
    return base.filter(PrecioDetalle.codigo_zona_fk.is_(None)).first()


def buscar_condicion_flete(db: Session, tercero, origen, destino, zona, cobertura, pago=None):
    """Replica TteCondicionFleteRepository::apiWindowsLiquidar."""
    if not tercero:
        return None
    base = db.query(CondicionFlete).filter(CondicionFlete.codigo_tercero_fk == tercero)
    if not base.first():
        return None
    if origen and destino:
        cf = base.filter(
            CondicionFlete.codigo_ciudad_origen_fk == origen,
            CondicionFlete.codigo_ciudad_destino_fk == destino,
        ).first()
        if cf:
            return cf
    if zona:
        cf = base.filter(CondicionFlete.codigo_zona_fk == zona).first()
        if cf:
            return cf
    if origen and cobertura and pago:
        cf = base.filter(
            CondicionFlete.codigo_ciudad_origen_fk == origen,
            CondicionFlete.codigo_cobertura_fk == cobertura,
            CondicionFlete.codigo_pago_fk == pago,
        ).first()
        if cf:
            return cf
    if origen and cobertura:
        cf = base.filter(
            CondicionFlete.codigo_ciudad_origen_fk == origen,
            CondicionFlete.codigo_cobertura_fk == cobertura,
        ).first()
        if cf:
            return cf
    if cobertura:
        cf = base.filter(
            CondicionFlete.codigo_ciudad_origen_fk.is_(None),
            CondicionFlete.codigo_ciudad_destino_fk.is_(None),
            CondicionFlete.codigo_cobertura_fk == cobertura,
        ).first()
        if cf:
            return cf
    # Sin origen se omite: "== None" se volvería IS NULL y traería otra condición
    if not origen:
        return None
    return base.filter(
        CondicionFlete.codigo_ciudad_origen_fk == origen,
        CondicionFlete.codigo_ciudad_destino_fk.is_(None),
        CondicionFlete.codigo_zona_fk.is_(None),
    ).first()


def buscar_condicion_manejo(db: Session, tercero, origen, destino, zona, cobertura, pago=None):
    """Replica TteCondicionManejoRepository::apiWindowsLiquidar."""
    if not tercero:
        return None
    base = db.query(CondicionManejo).filter(CondicionManejo.codigo_tercero_fk == tercero)
    if not base.first():
        return None
    if origen and destino:
        cm = base.filter(
            CondicionManejo.codigo_ciudad_origen_fk == origen,
            CondicionManejo.codigo_ciudad_destino_fk == destino,
        ).first()
        if cm:
            return cm
    if zona:
        cm = base.filter(CondicionManejo.codigo_zona_fk == zona).first()
        if cm:
            return cm
    if origen and cobertura and pago:
        cm = base.filter(
            CondicionManejo.codigo_ciudad_origen_fk == origen,
            CondicionManejo.codigo_cobertura_fk == cobertura,
            CondicionManejo.codigo_pago_fk == pago,
        ).first()
        if cm:
            return cm
    if origen and cobertura:
        cm = base.filter(
            CondicionManejo.codigo_ciudad_origen_fk == origen,
            CondicionManejo.codigo_cobertura_fk == cobertura,
        ).first()
        if cm:
            return cm
    if cobertura:
        cm = base.filter(
            CondicionManejo.codigo_ciudad_origen_fk.is_(None),
            CondicionManejo.codigo_ciudad_destino_fk.is_(None),
            CondicionManejo.codigo_cobertura_fk == cobertura,
        ).first()
        if cm:
            return cm
    # Sin origen se omite: "== None" se volvería IS NULL y traería otra condición
    if not origen:
        return None
    return base.filter(
        CondicionManejo.codigo_ciudad_origen_fk == origen,
        CondicionManejo.codigo_ciudad_destino_fk.is_(None),
        CondicionManejo.codigo_zona_fk.is_(None),
    ).first()


def condicion_especial(db: Session, tercero, origen, destino, precio, guia_tipo=None, producto=None):
    """Replica TteGuiaRepository::condicionEspecial de PHP.
    Devuelve None si el tercero no existe."""
    tercero_obj = db.query(Tercero).filter(Tercero.codigo_tercero_pk == tercero).first()
    if not tercero_obj:
        return None

    resultado = {
        "error": False,
        "error_mensaje": None,
        "condicion_especial_flete": False,
        "condicion_especial_manejo": False,
        "cobertura": None,
        "vr_peso": 0,
        "vr_unidad": 0,
        "descuento_peso": 0,
        "descuento_unidad": 0,
        "peso_minimo": 0,
        "peso_minimo_guia": 0,
        "flete_minimo": 0,
        "flete_minimo_guia": 0,
        "porcentaje_manejo": 0,
        "manejo_minimo_unidad": 0,
        "manejo_minimo_guia": 0,
        "reexpedicion": False,
    }

    pago = None
    if guia_tipo:
        tipo = db.query(GuiaTipo).filter(GuiaTipo.codigo_guia_tipo_pk == guia_tipo).first()
        if tipo:
            pago = tipo.codigo_pago_fk

    # Manejo base desde la condición del tercero
    condicion = tercero_obj.condicion
    if condicion:
        resultado["porcentaje_manejo"] = condicion.porcentaje_manejo or 0
        resultado["manejo_minimo_unidad"] = condicion.manejo_minimo_unidad or 0
        resultado["manejo_minimo_guia"] = condicion.manejo_minimo_despacho or 0

    zona = None
    ciudad_destino = db.query(Ciudad).filter(Ciudad.codigo_ciudad_pk == destino).first()
    if ciudad_destino:
        resultado["reexpedicion"] = bool(ciudad_destino.reexpedicion)
        zona = ciudad_destino.codigo_zona_fk

    if producto:
        precio_detalle = _buscar_precio_detalle(db, precio, origen, destino, producto, zona)
        if precio_detalle:
            resultado["vr_peso"] = precio_detalle.vr_peso or 0
            resultado["vr_unidad"] = precio_detalle.vr_unidad or 0
            resultado["cobertura"] = precio_detalle.codigo_cobertura_fk
            resultado["peso_minimo"] = precio_detalle.minimo or 0
    else:
        resultado["error"] = True
        resultado["error_mensaje"] = "Debe indicar el producto"

    cobertura = resultado["cobertura"]

    condicion_flete = buscar_condicion_flete(db, tercero, origen, destino, zona, cobertura, pago)
    if condicion_flete:
        resultado["condicion_especial_flete"] = True
        resultado["descuento_peso"] = condicion_flete.descuento_peso or 0
        resultado["descuento_unidad"] = condicion_flete.descuento_unidad or 0
        resultado["peso_minimo"] = condicion_flete.peso_minimo or 0
        resultado["peso_minimo_guia"] = condicion_flete.peso_minimo_guia or 0
        resultado["flete_minimo"] = condicion_flete.flete_minimo or 0
        resultado["flete_minimo_guia"] = condicion_flete.flete_minimo_guia or 0

    condicion_manejo = buscar_condicion_manejo(db, tercero, origen, destino, zona, cobertura, pago)
    if condicion_manejo:
        resultado["condicion_especial_manejo"] = True
        resultado["porcentaje_manejo"] = condicion_manejo.porcentaje or 0
        resultado["manejo_minimo_unidad"] = condicion_manejo.minimo_unidad or 0
        resultado["manejo_minimo_guia"] = condicion_manejo.minimo_despacho or 0

    return resultado


def liquidar(db: Session, tercero, condicion_id, precio, origen, destino, producto, zona, tipo_liquidacion, unidades, peso, volumen, declarado, pago=None):
    
    descuento_peso = 0
    porcentaje_manejo = 0
    manejo_minimo_unidad = 0
    manejo_minimo_despacho = 0
    peso_minimo_unidad = 0
    peso_minimo_despacho = 0
    flete_minimo_unidad = 0
    flete_minimo_despacho = 0

    flete = 0
    manejo = 0
    peso_facturado = peso
    if volumen > peso_facturado:
        peso_facturado = volumen
    cobertura = None

    # Condición base
    if condicion_id:
        condicion = db.query(Condicion).filter(Condicion.codigo_condicion_pk == condicion_id).first()
        if condicion:
            descuento_peso = condicion.descuento_peso or 0
            porcentaje_manejo = condicion.porcentaje_manejo or 0
            manejo_minimo_unidad = condicion.manejo_minimo_unidad or 0
            manejo_minimo_despacho = condicion.manejo_minimo_despacho or 0
            peso_minimo_unidad = condicion.peso_minimo or 0

    # Precio detalle (define cobertura)
    precio_detalle = _buscar_precio_detalle(db, precio, origen, destino, producto, zona)
    if precio_detalle:
        cobertura = precio_detalle.codigo_cobertura_fk

    # Condición flete (sobreescribe descuentos y mínimos)
    condicion_flete = buscar_condicion_flete(db, tercero, origen, destino, zona, cobertura, pago)
    if condicion_flete:
        descuento_peso = condicion_flete.descuento_peso or 0
        peso_minimo_unidad = condicion_flete.peso_minimo or 0
        peso_minimo_despacho = condicion_flete.peso_minimo_guia or 0
        flete_minimo_unidad = condicion_flete.flete_minimo or 0
        flete_minimo_despacho = condicion_flete.flete_minimo_guia or 0

    if peso_facturado < peso_minimo_unidad * unidades:
        peso_facturado = peso_minimo_unidad * unidades
    if peso_facturado < peso_minimo_despacho:
        peso_facturado = peso_minimo_despacho

    if precio_detalle:
        if tipo_liquidacion == "K":
            flete = peso_facturado * (precio_detalle.vr_peso or 0)
            if descuento_peso > 0:
                flete -= flete * descuento_peso / 100
        elif tipo_liquidacion == "U":
            flete = unidades * (precio_detalle.vr_unidad or 0)
        elif tipo_liquidacion == "A":
            flete = peso_facturado * (precio_detalle.vr_peso or 0)

        if unidades > 0:
            if flete_minimo_unidad > flete / unidades:
                flete = flete_minimo_unidad * unidades
        if flete_minimo_despacho > flete:
            flete = flete_minimo_despacho

    # Condición manejo
    condicion_manejo = buscar_condicion_manejo(db, tercero, origen, destino, zona, cobertura, pago)
    if condicion_manejo:
        porcentaje_manejo = condicion_manejo.porcentaje or 0
        manejo_minimo_unidad = condicion_manejo.minimo_unidad or 0
        manejo_minimo_despacho = condicion_manejo.minimo_despacho or 0

    manejo = declarado * porcentaje_manejo / 100
    if manejo_minimo_despacho > manejo:
        manejo = manejo_minimo_despacho
    if manejo_minimo_unidad * unidades > manejo:
        manejo = manejo_minimo_unidad * unidades

    return {
        "error": False,
        "flete": round(flete),
        "manejo": round(manejo),
        "peso_facturado": peso_facturado,
    }


# ---------------------------------------------------------------------------
# Entrega de guías (compartida por /tte/guia/entrega y la app móvil)
# ---------------------------------------------------------------------------

MAX_ARCHIVO_ENTREGA = 10 * 1024 * 1024  # 10 MB por imagen o firma
MAX_IMAGENES_ENTREGA = 10
MAX_TOTAL_ENTREGA = 30 * 1024 * 1024  # 30 MB sumando fotos y firma
_EXTENSIONES_IMAGEN = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


def usuario_autenticado(master_db: Session, current_user: dict) -> str:
    """Correo del usuario autenticado, truncado a 25 caracteres.
    JWT: viene en el claim email. API key (o token sin email): se busca en la BD master."""
    if current_user.get("email"):
        return current_user["email"][:25]
    sub = str(current_user.get("sub", ""))
    usuario_id = None
    if sub.isdigit():
        usuario_id = int(sub)
    else:
        key = master_db.query(ApiKey).filter(ApiKey.prefix == sub).first()
        if key:
            usuario_id = key.usuario_id
    user = master_db.query(User).filter(User.id == usuario_id).first() if usuario_id else None
    return (user.email if user else sub)[:25]


def parsear_datos_entrega(datos: str) -> GuiaEntregaRequest:
    """Valida el campo `datos` (JSON) del multipart de entrega."""
    try:
        return GuiaEntregaRequest.model_validate_json(datos)
    except ValidationError as e:
        # Mismo formato que un body normal: ubicacion "datos" y el campo con error
        raise RequestValidationError([{**err, "loc": ("datos", *err["loc"])} for err in e.errors(include_url=False)])


def _leer_archivo(archivo: UploadFile, campo: str, tipos: set[str]) -> bytes:
    """Lee el archivo subido validando tamaño y tipo real (por contenido, no por la extensión)."""
    data = archivo.file.read(MAX_ARCHIVO_ENTREGA + 1)
    if not data or len(data) > MAX_ARCHIVO_ENTREGA:
        raise HTTPException(status_code=400, detail=f"{campo}: vacío o supera el tamaño máximo de 10MB")
    if magic.from_buffer(data[:2048], mime=True) not in tipos:
        raise HTTPException(status_code=400, detail=f"{campo}: tipo de archivo no permitido")
    return data


def leer_archivos_entrega(imagenes: list[UploadFile], firma: UploadFile | None) -> tuple[list[bytes], bytes | None]:
    """Lee y valida fotos y firma antes de tocar la guía: uno inválido no deja la entrega a medias."""
    if len(imagenes) > MAX_IMAGENES_ENTREGA:
        raise HTTPException(status_code=400, detail=f"Máximo {MAX_IMAGENES_ENTREGA} imágenes por entrega")

    # Con el tamaño que registró el parser se rechaza el exceso antes de cargar archivos en memoria
    total = sum(archivo.size or 0 for archivo in [*imagenes, firma] if archivo)
    if total > MAX_TOTAL_ENTREGA:
        raise HTTPException(status_code=400, detail="Los archivos de la entrega superan el tamaño máximo total de 30MB")

    archivos_imagenes = [
        _leer_archivo(img, f"imagenes[{i}]", set(_EXTENSIONES_IMAGEN)) for i, img in enumerate(imagenes)
    ]
    archivo_firma = _leer_archivo(firma, "firma", {"image/png"}) if firma else None
    return archivos_imagenes, archivo_firma


def _subir_fichero(db: Session, guia: int, data: bytes, nombre: str, extension: str, mime: str,
                   directorio_base: str, carpeta: str, usuario: str, tipo: str = "G",
                   comprimido: bool = False) -> bool:
    """Registra el fichero de la guía y lo sube a Backblaze. Si la subida falla queda con error_carga.
    Tipo G (general) se descarga de la carpeta fichero/; F (firma) de firma/."""
    fichero = Fichero(
        codigo_fichero_tipo_fk=tipo,
        codigo_modelo_fk="TteGuia",
        codigo=str(guia),
        fecha=datetime.now(),
        nombre=nombre,
        extension=extension,
        tipo=mime,
        tamano=len(data),
        usuario=usuario[:25] if usuario else None,
        ui="M",
        comprimido=comprimido,
        directorio_base=directorio_base,
    )
    db.add(fichero)
    try:
        db.flush()
    except SQLAlchemyError:
        # La entrega ya está confirmada: un fallo al registrar el fichero no la revierte
        db.rollback()
        logger.exception("Error registrando el fichero %s de la guía %s", nombre, guia)
        return False
    try:
        b2_client.upload_file(f"{directorio_base}/{carpeta}/{fichero.codigo_fichero_pk}.{extension}", data, mime)
        ok = True
    except Exception:
        logger.exception("Error subiendo a Backblaze el fichero %s de la guía %s", fichero.codigo_fichero_pk, guia)
        fichero.error_carga = True
        ok = False
    db.commit()
    return ok


def registrar_entrega(db: Session, payload: GuiaEntregaRequest, archivos_imagenes: list[bytes],
                      archivo_firma: bytes | None, usuario: str) -> GuiaEntregaResponse:
    """Marca la guía como entregada, registra seguimientos, ubicación y despacho, y sube los archivos.
    Los archivos ya deben venir validados (leer_archivos_entrega); `usuario` es quien registra la entrega."""
    directorio_base = None
    if archivos_imagenes or archivo_firma:
        configuracion = db.query(Configuracion).first()
        directorio_base = configuracion.ruta_almacenamiento_servicio if configuracion else None
        if not directorio_base:
            raise HTTPException(status_code=400, detail="No está configurada la ruta del servicio documental")

    # Se bloquea la fila para que dos entregas simultáneas no cuenten doble en el despacho
    guia = db.query(Guia).filter(Guia.codigo_guia_pk == payload.guia).with_for_update().first()
    if not guia:
        raise HTTPException(status_code=404, detail="Guía no encontrada")
    if guia.estado_anulado:
        raise HTTPException(status_code=409, detail="La guía está anulada")
    if not guia.estado_despachado:
        raise HTTPException(status_code=409, detail="La guía no está despachada")
    if guia.estado_entregado:
        # entrega=true le indica a la app que la guía ya quedó entregada (p. ej. en un reintento)
        raise HTTPException(
            status_code=409, detail={"message": "La guía ya fue entregada anteriormente", "entrega": True}
        )

    ahora = datetime.now()
    fecha_entrega = payload.fecha_entrega or ahora

    guia.fecha_entrega = fecha_entrega
    guia.estado_entregado = True
    guia.usuario_entrega = usuario

    # Llaves en camelCase: el formato de impresión las lee así del seguimiento FIRMA
    datos_adicionales = {
        llave: valor for llave, valor in {
            "recibe": payload.recibe,
            "recibeParentesco": payload.recibe_parentesco,
            "recibeNumeroIdentificacion": payload.recibe_numero_identificacion,
            "recibeCelular": payload.recibe_celular,
        }.items() if valor
    }
    datos_seguimiento = json.dumps(datos_adicionales) if datos_adicionales else None

    def seguimiento(tipo: str, **extra) -> Seguimiento:
        return Seguimiento(
            codigo_guia_fk=guia.codigo_guia_pk,
            codigo_seguimiento_tipo_fk=tipo,
            fecha=ahora,
            fecha_seguimiento=fecha_entrega,
            usuario=usuario[:50],
            **extra,
        )

    comentario = " ".join(filter(None, ["ENTREGA APP MOVIL", payload.usuario_nombre, payload.usuario_correo]))
    db.add(seguimiento(
        "ENTREGA",
        comentario=comentario[:300],
        datos=datos_seguimiento,
        latitud=payload.latitud or 0,
        longitud=payload.longitud or 0,
    ))
    if archivos_imagenes:
        guia.estado_predigitalizado = True
        guia.estado_digitalizado = True
        db.add(seguimiento("DIGITALIZACION"))
    if archivo_firma:
        guia.estado_firma = True
        db.add(seguimiento("FIRMA", datos=datos_seguimiento))

    if payload.latitud is not None and payload.longitud is not None:
        db.add(Ubicacion(
            codigo_guia_fk=guia.codigo_guia_pk,
            codigo_despacho_fk=guia.codigo_despacho_fk,
            fecha=ahora,
            usuario=usuario[:25],
            latitud=payload.latitud,
            longitud=payload.longitud,
            velocidad=payload.velocidad or 0,
            altitud=payload.altitud or 0,
            exactitud=payload.exactitud or 0,
            exactitud_altitud=payload.exactitud_altitud or 0,
        ))

    # El despacho va acumulando las guías entregadas
    if guia.codigo_despacho_fk:
        db.query(Despacho).filter(Despacho.codigo_despacho_pk == guia.codigo_despacho_fk).update(
            {Despacho.cantidad_entregada: Despacho.cantidad_entregada + 1}, synchronize_session=False
        )

    db.commit()

    # Los archivos se suben después de confirmar la entrega; si fallan, la entrega se mantiene
    errores = 0
    for data in archivos_imagenes:
        mime = magic.from_buffer(data[:2048], mime=True)
        comprimido = False
        try:
            jpg = comprimir_imagen(data)
            # Las fotos quedan en JPG; un JPG original más liviano que el recomprimido se deja tal cual
            if not (mime == "image/jpeg" and len(data) <= len(jpg)):
                data, mime, comprimido = jpg, "image/jpeg", True
        except Exception:
            logger.exception("Error comprimiendo imagen de la guía %s; se sube la original", guia.codigo_guia_pk)
        extension = _EXTENSIONES_IMAGEN[mime]
        if not _subir_fichero(db, guia.codigo_guia_pk, data, f"{guia.codigo_guia_pk}.{extension}", extension,
                              mime, directorio_base, "fichero", usuario, comprimido=comprimido):
            errores += 1
    if archivo_firma:
        nombre = f"{random.randint(100000, 999999)}_{guia.codigo_guia_pk}.png"
        if not _subir_fichero(db, guia.codigo_guia_pk, archivo_firma, nombre, "png", "image/png",
                              directorio_base, "firma", usuario, tipo="F"):
            errores += 1

    db.refresh(guia)
    return GuiaEntregaResponse(
        codigo_guia_pk=guia.codigo_guia_pk,
        estado_entregado=guia.estado_entregado,
        fecha_entrega=guia.fecha_entrega,
        estado_digitalizado=guia.estado_digitalizado,
        estado_firma=guia.estado_firma,
        ficheros_con_error=errores,
    )

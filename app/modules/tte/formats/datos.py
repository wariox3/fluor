"""
Datos listos para imprimir guías y rótulos.

Se cargan una sola vez por impresión y los formatos solo leen de aquí, así ningún
formato dispara consultas extra. Los valores van tal cual están en la guía junto con las
banderas para ocultarlos: cada formato de holmio aplica su propia regla.
"""
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session, joinedload

from app.core.backblaze import b2_client
from app.core.utils import fmt_numero
from app.modules.doc.models.fichero import Fichero
from app.modules.gen.models.configuracion import Configuracion
from app.modules.gen.models.imagen import Imagen
from app.modules.tte.models.guia import Guia
from app.modules.tte.models.seguimiento import Seguimiento

logger = logging.getLogger(__name__)

MAXIMO_GUIAS = 100


def numero(valor: float) -> str:
    """Como `number_format()` de PHP, que usan los formatos de holmio: coma de miles."""
    return fmt_numero(round(valor or 0), separador=",")


@dataclass
class EmpresaImpresion:
    nombre: str = ""
    nit: str = ""
    digito_verificacion: str = ""
    direccion: str = ""
    telefono: str = ""
    correo: str = ""
    sitio_web: str = ""
    logo: bytes | None = None
    codigo_formato_guia_web: str | None = None
    codigo_formato_rotulo: str | None = None
    mostrar_valor_declarado_guia: bool = False
    ocultar_valores_formato_corriente: bool = False
    ruta_almacenamiento: str = ""   # carpeta base en Backblaze (firmas de entrega)


@dataclass
class GuiaImpresion:
    codigo: int
    tipo_nombre: str = ""
    tipo_mensaje_formato: str = ""   # leyenda del tipo de guía (resolución DIAN, etc.)
    codigo_pago: str = ""          # forma de pago del tipo de guía (COR, CRE, …)
    forma_pago_tercero: str = ""   # forma de pago del cliente
    fecha_ingreso: datetime | None = None
    fecha_entrega: datetime | None = None

    remitente_nombre: str = ""
    remitente_identificacion: str = ""
    remitente_direccion: str = ""
    remitente_telefono: str = ""
    tercero_direccion: str = ""
    tercero_telefono: str = ""

    destinatario_nombre: str = ""
    destinatario_tipo_identificacion: str = ""
    destinatario_identificacion: str = ""
    destinatario_direccion: str = ""
    destinatario_telefono: str = ""

    ciudad_origen_codigo: str = ""
    ciudad_origen_nombre: str = ""
    ciudad_destino_codigo: str = ""
    ciudad_destino_nombre: str = ""

    documento_cliente: str = ""
    relacion_cliente: str = ""
    zona: str = ""
    franja: str = ""
    numero_factura: str = ""
    servicio_nombre: str = ""
    producto_nombre: str = ""
    empaque_nombre: str = ""
    comentario: str = ""
    operacion_ingreso: str = ""
    usuario: str = ""

    unidades: float = 0
    peso_real: float = 0
    peso_volumen: float = 0
    peso_facturado: float = 0

    vr_declara: float = 0
    vr_flete: float = 0
    vr_manejo: float = 0
    vr_otros: float = 0
    vr_recaudo: float = 0
    vr_cobro_entrega: float = 0

    factura: bool = False                   # guía marcada para facturar
    tercero_ocultar_valores: bool = False   # el cliente no quiere ver valores en la guía
    tercero_ocultar_declarado: bool = False

    devolucion: bool = False
    devolver_documento_cliente: bool = False
    contenido_verificado: bool = False
    firma: bytes | None = None   # imagen de la firma de entrega
    recibe: str = ""             # identificación y nombre de quien recibió


def cargar_empresa(db: Session) -> EmpresaImpresion:
    configuracion = db.query(Configuracion).filter(Configuracion.codigo_configuracion_pk == 1).first()
    logo = db.query(Imagen).filter(Imagen.codigo_imagen_pk == "LOGO").first()
    if not configuracion:
        return EmpresaImpresion(logo=_bytes(logo))
    return EmpresaImpresion(
        nombre=_t(configuracion.nombre),
        nit=_t(configuracion.nit),
        digito_verificacion=_t(configuracion.digito_verificacion),
        direccion=_t(configuracion.direccion),
        telefono=_t(configuracion.telefono),
        correo=_t(configuracion.correo),
        sitio_web=_t(configuracion.sitio_web),
        logo=_bytes(logo),
        codigo_formato_guia_web=configuracion.codigo_formato_guia_web,
        codigo_formato_rotulo=configuracion.codigo_formato_rotulo,
        mostrar_valor_declarado_guia=bool(configuracion.mostrar_valor_declarado_guia),
        ocultar_valores_formato_corriente=bool(configuracion.ocultar_valores_formato_corriente),
        ruta_almacenamiento=_t(configuracion.ruta_almacenamiento_servicio),
    )


def cargar_guias(db: Session, numero_desde: int, numero_hasta: int) -> list[Guia]:
    """Guías no anuladas del rango (como holmio). Trae una de más para validar el máximo."""
    return (
        db.query(Guia)
        .options(
            joinedload(Guia.tercero),
            joinedload(Guia.adquiriente),
            joinedload(Guia.guia_tipo),
            joinedload(Guia.producto),
            joinedload(Guia.empaque),
            joinedload(Guia.servicio),
            joinedload(Guia.ciudad_origen),
            joinedload(Guia.ciudad_destino),
            joinedload(Guia.operacion_ingreso),
        )
        .filter(
            Guia.codigo_guia_pk >= numero_desde,
            Guia.codigo_guia_pk <= numero_hasta,
            Guia.estado_anulado.is_(False),
        )
        .order_by(Guia.codigo_guia_pk)
        .limit(MAXIMO_GUIAS + 1)
        .all()
    )


def preparar_guias(db: Session, guias: list[Guia], empresa: EmpresaImpresion,
                   con_firma: bool = False) -> list[GuiaImpresion]:
    firmas = _firmas(db, guias, empresa) if con_firma else {}
    recibe = _recibe(db, guias) if con_firma else {}
    return [_preparar(g, empresa, firmas.get(g.codigo_guia_pk), recibe.get(g.codigo_guia_pk, ""))
            for g in guias]


def _preparar(g: Guia, empresa: EmpresaImpresion, firma: bytes | None, recibe: str) -> GuiaImpresion:
    tercero, tipo = g.tercero, g.guia_tipo
    return GuiaImpresion(
        codigo=g.codigo_guia_pk,
        tipo_nombre=_t(tipo.nombre if tipo else ""),
        tipo_mensaje_formato=_t(tipo.mensaje_formato if tipo else ""),
        codigo_pago=_t(tipo.codigo_pago_fk if tipo else ""),
        forma_pago_tercero=_t(tercero.codigo_forma_pago_fk if tercero else ""),
        fecha_ingreso=g.fecha_ingreso,
        fecha_entrega=g.fecha_entrega,
        remitente_nombre=_t(g.nombre_remitente),
        remitente_identificacion=_t(tercero.numero_identificacion if tercero else ""),
        remitente_direccion=_t(g.direccion_remitente),
        remitente_telefono=_t(g.telefono_remitente),
        tercero_direccion=_t(tercero.direccion if tercero else ""),
        tercero_telefono=_t(tercero.telefono if tercero else ""),
        destinatario_nombre=_t(g.nombre_destinatario),
        destinatario_tipo_identificacion=_t(g.codigo_identificacion_destinatario_fk),
        destinatario_identificacion=_t(g.numero_identificacion_destinatario),
        destinatario_direccion=_t(g.direccion_destinatario),
        destinatario_telefono=_t(g.telefono_destinatario),
        ciudad_origen_codigo=_t(g.codigo_ciudad_origen_fk),
        ciudad_origen_nombre=_t(g.ciudad_origen.nombre if g.ciudad_origen else ""),
        ciudad_destino_codigo=_t(g.codigo_ciudad_destino_fk),
        ciudad_destino_nombre=_t(g.ciudad_destino.nombre if g.ciudad_destino else ""),
        documento_cliente=_t(g.documento_cliente),
        relacion_cliente=_t(g.relacion_cliente),
        zona=_t(g.codigo_zona_fk),
        franja=_t(g.franja),
        numero_factura=_t(g.numero_factura),
        servicio_nombre=_t(g.servicio.nombre if g.servicio else ""),
        producto_nombre=_t(g.producto.nombre if g.producto else ""),
        empaque_nombre=_t(g.empaque.nombre if g.empaque else ""),
        comentario=_t(g.comentario),
        operacion_ingreso=_t(g.codigo_operacion_ingreso_fk),
        usuario=_t(g.usuario),
        unidades=_n(g.unidades),
        peso_real=_n(g.peso_real),
        peso_volumen=_n(g.peso_volumen),
        peso_facturado=_n(g.peso_facturado),
        vr_declara=_n(g.vr_declara),
        vr_flete=_n(g.vr_flete),
        vr_manejo=_n(g.vr_manejo),
        vr_otros=_n(g.vr_otros),
        vr_recaudo=_n(g.vr_recaudo),
        vr_cobro_entrega=_n(g.vr_cobro_entrega),
        factura=bool(g.factura),
        tercero_ocultar_valores=bool(tercero and tercero.ocultar_valores_guia),
        tercero_ocultar_declarado=bool(tercero and tercero.ocultar_valor_declarado),
        devolucion=bool(g.estado_devolucion),
        devolver_documento_cliente=bool(g.devolver_documento_cliente),
        contenido_verificado=bool(g.contenido_verificado),
        firma=firma,
        recibe=recibe,
    )


def _firmas(db: Session, guias: list[Guia], empresa: EmpresaImpresion) -> dict[int, bytes]:
    """Imagen de la firma de entrega de cada guía, descargada de Backblaze."""
    codigos = [str(g.codigo_guia_pk) for g in guias]
    ficheros = (
        db.query(Fichero)
        .filter(
            Fichero.codigo_fichero_tipo_fk == "F",
            Fichero.codigo_modelo_fk == "TteGuia",
            Fichero.codigo.in_(codigos),
        )
        .order_by(Fichero.codigo_fichero_pk)
        .all()
    )
    firmas: dict[int, bytes] = {}
    for fichero in ficheros:
        guia = int(fichero.codigo)
        base = fichero.directorio_base or empresa.ruta_almacenamiento
        if guia in firmas or not base:
            continue
        try:
            contenido, _ = b2_client.download_file(f"{base}/firma/{fichero.codigo_fichero_pk}.{fichero.extension}")
            firmas[guia] = contenido
        except Exception:
            logger.warning("No se pudo descargar la firma de la guía %s", guia, exc_info=True)
    return firmas


def _recibe(db: Session, guias: list[Guia]) -> dict[int, str]:
    """Identificación y nombre de quien recibió, tomados del seguimiento FIRMA."""
    seguimientos = (
        db.query(Seguimiento.codigo_guia_fk, Seguimiento.datos)
        .filter(
            Seguimiento.codigo_guia_fk.in_([g.codigo_guia_pk for g in guias]),
            Seguimiento.codigo_seguimiento_tipo_fk == "FIRMA",
        )
        .order_by(Seguimiento.codigo_seguimiento_pk)
        .all()
    )
    recibe: dict[int, str] = {}
    for guia, datos in seguimientos:
        if guia in recibe or not datos:
            continue
        try:
            entrega = json.loads(datos)
        except (TypeError, ValueError):
            continue
        if not isinstance(entrega, dict):
            continue
        partes = [_t(entrega.get("recibeNumeroIdentificacion")), _t(entrega.get("recibe"))]
        texto = " ".join(p for p in partes if p)
        if texto:
            recibe[guia] = texto
    return recibe


def _t(valor: Any) -> str:
    return "" if valor is None else str(valor).strip()


def _n(valor: Any) -> float:
    try:
        return float(valor or 0)
    except (TypeError, ValueError):
        return 0.0


def _bytes(imagen: Any) -> bytes | None:
    if imagen is None or not imagen.imagen:
        return None
    return bytes(imagen.imagen)

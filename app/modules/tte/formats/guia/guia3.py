"""
Guía formato 3 — A4 con 3 copias (REMITENTE / EMPRESA / DESTINATARIO).
Réplica de holmio `src/Formato/Transporte/Guia3.php`; las coordenadas son las mismas (mm).
"""
from pathlib import Path

from reportlab.lib.pagesizes import A4

from app.core.pdf_lienzo import FormatoPdf, Lienzo, imagen_lector
from app.core.utils import fmt_cantidad
from app.modules.tte.formats.datos import EmpresaImpresion, GuiaImpresion, numero
from app.modules.tte.formats.guia import registro

_VIGILADO = Path(__file__).parents[4] / "static" / "img" / "vigilado_supertransporte_2024.png"

_COPIAS = [
    # (y de referencia, etiqueta, y etiqueta, y datos de quien recibe, y marca devolución)
    (12, "REMITENTE", 89, 82, 90),
    (108, "EMPRESA", 181, 178, 190),
    (204, "DESTINATARIO", 278, 273, 285),
]

_TEXTO_LEGAL = [
    "El contrato de transporte se rige por los articulos 1008 al 1035 del C. de C y respondemos "
    "unicamente hasta por el valor informado.",
    "Firmada la remision no devuelva la mercancia sin exigir los documentos que haya firmado. "
    "Nota: No se aceptan reclamaciones despues",
    "de 90 dias de haberse generado la factura. OPE-03-D02 -Ministerio de Transporte Res 322 de "
    "Noviembre 4 de 2014",
]


@registro.registrar
class Guia3(FormatoPdf):
    codigo = 3
    nombre = "A4 con 3 copias (remitente, empresa, destinatario)"
    tamano = A4
    usa_firma = True

    def __init__(self):
        self._vigilado = imagen_lector(_VIGILADO)

    def dibujar(self, l: Lienzo, guia: GuiaImpresion, empresa: EmpresaImpresion, pagina: int) -> None:
        logo = imagen_lector(empresa.logo)
        firma = imagen_lector(guia.firma)
        for y, etiqueta, y_etiqueta, y_recibe, y_devolucion in _COPIAS:
            self._copia(l, guia, empresa, y, logo, firma, y_recibe, y_devolucion)
            l.fuente(7, negrita=True)
            l.celda(75, y_etiqueta, 55, 4, etiqueta, alinear="C")

    def _copia(self, l: Lienzo, g: GuiaImpresion, e: EmpresaImpresion, y: float,
               logo, firma, y_recibe: float, y_devolucion: float) -> None:
        # ── Imágenes, códigos y firma ─────────────────────────────────────────
        l.imagen(logo, 6, y - 5, 16, 16)
        l.imagen(self._vigilado, 5, y + 74, 28, 10)
        l.qr(g.codigo, 66, y - 5, 15)
        l.codigo_barras(g.codigo, 166, y + 2, 32, 8)
        l.imagen(firma, 166, y + 56, 28, 20)
        if g.recibe:
            l.fuente(8)
            l.texto(90, y_recibe, g.recibe[:38])

        if g.devolucion:
            l.fuente(50, negrita=True)
            l.color_texto(200, 200, 200)
            l.texto_rotado(70, y_devolucion, "DEVOLUCIÓN", 38)
            l.color_texto(0, 0, 0)

        # ── Encabezado ────────────────────────────────────────────────────────
        l.fuente(8, negrita=True)
        l.celda(168, y - 5, 30, 4, g.tipo_nombre, alinear="C")
        l.fuente(7, negrita=True)
        l.celda(174, y - 2, 15, 4, g.codigo, alinear="C")
        l.fuente(10, negrita=True)
        l.texto(87, y - 2, e.nombre)
        l.fuente(8)
        l.texto(87, y + 1, f"NIT {e.nit}-{e.digito_verificacion}")
        l.texto(87, y + 4, f"{e.direccion} TEL: {e.telefono}")
        l.texto(87, y + 7, e.correo)

        # ── Fila 1: remitente, origen, destino, doc cliente, forma de pago ────
        l.rect(5, y + 11, 83, 13)
        l.fuente(6, negrita=True)
        l.celda(5, y + 11, 60, 5, "REMITENTE IDENTIFICACIÓN NOMBRE DIRECCIÓN")
        l.fuente(6)
        l.celda(5, y + 15, 60, 4, l.ajustar(g.remitente_nombre, 56))
        l.celda(65, y + 15, 15, 4, f"NIT/CC {g.remitente_identificacion}")
        # La dirección se recorta antes del teléfono (x=40) para que no se monten.
        l.celda(5, y + 19, 10, 4, l.ajustar(g.remitente_direccion, 33))
        l.celda(40, y + 19, 10, 4, l.ajustar(g.remitente_telefono, 46))

        self._ciudad(l, 88, y, 34, "POBLACIÓN ORIGEN", g.ciudad_origen_codigo, g.ciudad_origen_nombre)
        self._ciudad(l, 122, y, 35, "POBLACIÓN DESTINO", g.ciudad_destino_codigo, g.ciudad_destino_nombre)

        l.rect(157, y + 11, 28, 13)
        l.fuente(6, negrita=True)
        l.celda(157, y + 11, 25, 5, "DOC CLIENTE", alinear="C")
        l.fuente(6)
        l.celda(157, y + 15, 25, 5, l.ajustar(g.documento_cliente, 26))

        l.rect(185, y + 11, 17, 13)
        l.fuente(6, negrita=True)
        l.celda(181, y + 11, 25, 5, "FORMA PAGO", alinear="C")
        l.fuente(6)
        l.celda(181, y + 15, 25, 5, g.forma_pago_tercero, alinear="C")

        # ── Fila 2: destinatario, fechas, relación, zona ──────────────────────
        l.rect(5, y + 24, 83, 14)
        l.fuente(6, negrita=True)
        l.celda(5, y + 25, 75, 4, "DESTINATARIO NOMBRE DIRECCIÓN TELÉFONO")
        l.fuente(6)
        l.celda(5, y + 29, 60, 4, l.ajustar(g.destinatario_nombre, 56))
        l.celda(65, y + 29, 15, 4, f"CC/NIT {g.destinatario_identificacion}")
        l.celda(5, y + 33, 45, 5, l.ajustar(g.destinatario_direccion, 56))
        l.celda(65, y + 33, 30, 4, l.ajustar(g.destinatario_telefono, 21))

        l.rect(88, y + 24, 36, 14)
        l.fuente(6, negrita=True)
        l.celda(88, y + 25, 30, 4, "FECHA ELABORACIÓN")
        self._fecha(l, y + 29, y + 33, (88, 95, 105), g.fecha_ingreso)

        l.rect(124, y + 24, 27, 14)
        l.fuente(6, negrita=True)
        l.celda(124, y + 24, 25, 4, "FECHA ENTREGA")
        self._fecha(l, y + 29, y + 33, (124, 128, 133), g.fecha_entrega)

        l.rect(151, y + 24, 34, 8)
        l.fuente(6, negrita=True)
        l.celda(145, y + 24, 30, 4, "RELACIÓN", alinear="C")  # holmio la deja vacía

        l.rect(185, y + 24, 17, 8)
        l.fuente(6, negrita=True)
        l.celda(188, y + 24, 10, 4, "ZONA", alinear="C")
        l.fuente(6)
        l.celda(188, y + 28, 10, 4, g.zona, alinear="C")

        # ── Bloque 3: declaración, valores y medidas ──────────────────────────
        l.rect(5, y + 38, 83, 8)
        l.fuente(6, negrita=True)
        l.celda(5, y + 38, 80, 4, "EL REMITENTE DECLARA QUE ESTE DESPACHO CONTIENE UNICAMENTE")

        vr_declara, vr_flete, vr_manejo, vr_total = self._valores(g, e)
        # Columna de valores: (etiqueta, y caja, alto de celda, valor, valor en negrita)
        for etiqueta, dy, alto, valor, negrita in [
            ("VALOR DECLARADO", 46, 3, vr_declara, False),
            ("COSTO MANEJO", 51, 3, vr_manejo, False),
            ("FLETE", 56, 4, vr_flete, False),
            ("OTROS", 61, 4, g.vr_otros, False),
            ("TOTAL:", 66, 4, vr_total, True),
        ]:
            l.rect(5, y + dy, 23, 5)
            l.fuente(4, negrita=True)
            l.celda(5, y + dy, 22, alto, etiqueta)
            l.fuente(6, negrita=negrita)
            l.celda(23, y + dy + 2, 5, alto, numero(valor), alinear="R")

        # Medidas: caja (x, y, alto), celda etiqueta (x, ancho), celda valor (x, dy, ancho)
        for (x, dy, alto), (x_et, ancho_et), (x_val, dy_val, ancho_val), etiqueta, valor in [
            ((28, 46, 8), (32, 22), (32, 49, 20), "UNIDADES", fmt_cantidad(g.unidades)),
            ((58, 46, 8), (60, 25), (60, 49, 25), "PESO REAL", numero(g.peso_real)),
            ((28, 54, 8), (31, 25), (28, 58, 30), "PRODUCTO", l.ajustar(g.producto_nombre, 28)),
            ((58, 54, 8), (60, 25), (60, 58, 25), "PESO VOLUMEN", numero(g.peso_volumen)),
            ((28, 62, 9), (31, 25), (28, 66, 30), "RECAUDO", numero(g.vr_cobro_entrega)),
            ((58, 62, 9), (60, 25), (60, 66, 25), "PESO COBRADO", numero(g.peso_facturado)),
        ]:
            l.rect(x, y + dy, 30, alto)
            l.fuente(6, negrita=True)
            l.celda(x_et, y + dy, ancho_et, 4, etiqueta, alinear="C")
            l.fuente(9 if etiqueta == "RECAUDO" else 6)
            l.celda(x_val, y + dy_val, ancho_val, 4, valor, alinear="C")

        # ── Novedades ─────────────────────────────────────────────────────────
        l.rect(88, y + 38, 63, 4)
        l.fuente(4, negrita=True)
        l.celda(88, y + 38, 60, 4, "NOVEDADES", alinear="C")
        l.rect(88, y + 42, 63, 12)
        l.rect(130, y + 42.5, 10, 3, relleno=(255, 255, 255), borde=False)
        l.celda(130, y + 42.5, 10, 3, "OTROS")
        l.fuente(4)
        for dy, texto, borde in [
            (42, "DIRECCIÓN ERRADA", "LTR"),
            (45, "DESTINATARIO NO RECIBE / NO ESTA", "LR"),
            (48, "DESTINATARIO DESCONOCIDO", "LR"),
            (51, "OTROS", "LBR"),
        ]:
            l.celda(88, y + dy, 34, 3, texto, borde=borde)
            l.rect(122, y + dy, 8, 3)

        # ── Factura y servicio ────────────────────────────────────────────────
        l.rect(151, y + 32, 34, 10)
        l.fuente(6, negrita=True)
        l.celda(150, y + 32, 30, 4, "NÚMERO FACTURA", alinear="C")
        l.fuente(6)
        l.celda(145, y + 37, 30, 4, g.numero_factura, alinear="C")

        l.rect(185, y + 32, 17, 10)
        l.fuente(6, negrita=True)
        l.celda(178, y + 32, 30, 4, "SERVICIO", alinear="C")
        l.fuente(6)
        l.celda(178, y + 37, 30, 4, l.ajustar(g.servicio_nombre, 16), alinear="C")

        # ── Observaciones ─────────────────────────────────────────────────────
        l.rect(88, y + 54, 63, 8)
        if g.comentario:
            # Solo la etiqueta va en negrita; el comentario sigue en la misma línea.
            etiqueta = "OBSERVACIONES: "
            l.fuente(5.5, negrita=True)
            ancho_etiqueta = l.ancho_texto(etiqueta)
            l.celda(88, y + 54, 65, 2.6, etiqueta)
            l.fuente(5.5)
            disponible = 65 - 2 * l.MARGEN_CELDA - ancho_etiqueta
            palabras = g.comentario[:180].split()
            primera = ""
            while palabras and l.ancho_texto(f"{primera} {palabras[0]}".strip()) <= disponible:
                primera = f"{primera} {palabras.pop(0)}".strip()
            l.celda(88 + ancho_etiqueta, y + 54, disponible, 2.6, primera)
            l.multicelda(88, y + 56.6, 65, 2.6, " ".join(palabras), max_lineas=2)

        # ── Entrega y control ─────────────────────────────────────────────────
        l.rect(151, y + 42, 51, 12)
        l.fuente(6, negrita=True)
        l.celda(153, y + 42, 10, 4, "ENTREGADO POR")

        l.fuente(4, negrita=True)
        for x, ancho, texto in [(151, 16, "LEGALIZADO"), (167, 18, "ESCANEADA"), (185, 17, "CARTAPORTE:")]:
            l.rect(x, y + 54, ancho, 8)
            l.celda(x, y + 54, ancho, 4, texto, borde=1, alinear="C")

        l.rect(88, y + 62, 63, 9)
        l.fuente(5, negrita=True)
        l.celda(88, y + 62, 60, 4, "NOMBRE Y CÉDULA REMITENTE/DESTINATARIO", alinear="C")
        l.rect(151, y + 62, 51, 9)
        l.celda(151, y + 62, 55, 4, "FIRMA Y CÉDULA RECIBE", alinear="C")

        l.fuente(4)
        for i, linea in enumerate(_TEXTO_LEGAL):
            l.celda(115, y + 71 + 2 * i, 80, 2, linea)

    @staticmethod
    def _valores(g: GuiaImpresion, e: EmpresaImpresion) -> tuple[float, float, float, float]:
        """Valor declarado, flete, manejo y total con las reglas de ocultamiento de Guia3."""
        vr_flete, vr_manejo = g.vr_flete, g.vr_manejo
        vr_total = g.vr_flete + g.vr_manejo + g.vr_otros
        vr_declara = g.vr_declara if e.mostrar_valor_declarado_guia else 0
        if g.tercero_ocultar_declarado and g.codigo_pago == "COR":
            vr_declara = 0
        if g.tercero_ocultar_valores or (e.ocultar_valores_formato_corriente and g.codigo_pago == "COR"):
            vr_flete = vr_manejo = vr_total = 0
        return vr_declara, vr_flete, vr_manejo, vr_total

    @staticmethod
    def _ciudad(l: Lienzo, x: float, y: float, ancho: float, titulo: str, codigo: str, nombre: str) -> None:
        l.rect(x, y + 11, ancho, 13)
        l.fuente(6, negrita=True)
        l.celda(x, y + 11, ancho, 4, titulo)
        l.fuente(6)
        l.celda(x, y + 15, ancho, 4, codigo)
        l.celda(x, y + 19, ancho, 4, l.ajustar(nombre, ancho - 2))

    @staticmethod
    def _fecha(l: Lienzo, y_valor: float, y_rotulo: float, columnas: tuple[float, float, float], fecha) -> None:
        l.fuente(6)
        if fecha:
            for x, parte in zip(columnas, (fecha.strftime("%d"), fecha.strftime("%m"), fecha.strftime("%Y"))):
                l.celda(x, y_valor, 10, 4, parte)
        for x, rotulo in zip(columnas, ("DD", "MM", "AAAA")):
            l.celda(x, y_rotulo, 10, 4, rotulo)

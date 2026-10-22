"""
Guía formato 2 — etiqueta 100×100 mm, una copia por guía.
Réplica de holmio `src/Formato/Transporte/Guia2.php`; las coordenadas son las mismas (mm).
"""
from reportlab.lib.units import mm

from app.core.pdf_lienzo import FormatoPdf, Lienzo
from app.core.utils import ahora_local, fmt_cantidad
from app.modules.tte.formats.datos import EmpresaImpresion, GuiaImpresion, numero
from app.modules.tte.formats.guia import registro

_BLANCO = (255, 255, 255)
_GRIS = (200, 200, 200)
_NEGRO = (0, 0, 0)


@registro.registrar
class Guia2(FormatoPdf):
    codigo = 2
    nombre = "Etiqueta 100×100 mm"
    tamano = (100 * mm, 100 * mm)

    def dibujar(self, l: Lienzo, g: GuiaImpresion, e: EmpresaImpresion, pagina: int) -> None:
        l.qr(g.codigo, 74, 6, 20)

        # ── Encabezado ────────────────────────────────────────────────────────
        l.fuente(10, negrita=True)
        l.celda(4, 6, 80, 5, l.ajustar(e.nombre, 68))
        l.fuente(8, negrita=True)
        l.celda(4, 11, 80, 5, f"NIT {e.nit}-{e.digito_verificacion}  {e.sitio_web}")
        l.fuente(10, negrita=True)
        l.celda(4, 16, 30, 5, g.tipo_nombre)

        l.rect(55, 16, 16, 4)
        l.rect(55, 20, 16, 8)
        l.texto(58, 19, "ZONA")
        l.texto(57, 26, l.ajustar(g.franja, 14))

        l.celda(4, 20, 30, 5, f"GUIA No. {g.codigo}")
        fecha = g.fecha_ingreso.strftime("%y-%m-%d %H:%M") if g.fecha_ingreso else ""
        l.celda(4, 24, 30, 5, f"FECHA: {fecha}")

        # En holmio este aviso queda debajo de las celdas de origen y destino, que lo tapan.
        l.fuente(6.5, negrita=True)
        if g.devolver_documento_cliente and g.codigo_pago == "COR":
            l.texto(13, 34, "* DEVOLVER DOCUMENTO ADJUNTO FIRMADO Y SELLADO *")

        for x_titulo, ancho_titulo, titulo, x_valor, valor in [
            (5, 12, "ORIGEN:", 17, g.ciudad_origen_nombre),
            (50, 13, "DESTINO:", 63, g.ciudad_destino_nombre[:22]),
        ]:
            l.fuente(7, negrita=True)
            l.celda(x_titulo, 31, ancho_titulo, 5, titulo, borde="TLB", relleno=_BLANCO)
            l.fuente(7)
            l.celda(x_valor, 31, 34, 5, l.ajustar(valor, 32), borde="TRB", relleno=_BLANCO)

        # ── Remitente ─────────────────────────────────────────────────────────
        l.rect(5, 36, 92, 10)
        self._textos(l, True, [(6, 39, "REMITE:"), (70, 39, "NIT:"), (6, 42, "DIR:"), (70, 42, "TEL:"), (6, 45, "DOCUMENTO:")])
        self._textos(l, False, [
            (18, 39, g.remitente_nombre[:33], 51), (76, 39, g.remitente_identificacion),
            (13, 42, g.remitente_direccion, 56), (76, 42, g.remitente_telefono),
            (24, 45, g.documento_cliente),
        ])

        # ── Destinatario ──────────────────────────────────────────────────────
        l.rect(5, 46, 92, 10)
        self._textos(l, True, [(6, 50, "DESTINO:"), (70, 50, "DOC:"), (6, 54, "DIR:"), (70, 54, "TEL:")])
        identificacion = ""
        if g.destinatario_tipo_identificacion and g.destinatario_identificacion:
            identificacion = f"{g.destinatario_tipo_identificacion} {g.destinatario_identificacion[:12]}"
        self._textos(l, False, [
            (18, 50, g.destinatario_nombre[:32], 51), (77, 50, identificacion),
            (13, 54, g.destinatario_direccion[:41], 56), (76, 54, g.destinatario_telefono[:10]),
        ])

        # ── Liquidación ───────────────────────────────────────────────────────
        vr_flete, vr_manejo, vr_total, vr_declara = self._valores(g)
        l.rect(5, 56, 44, 5)
        l.fuente(7, negrita=True)
        l.texto(6, 59, "LIQUIDACION")
        l.rect(5, 61, 44, 18)
        for y, titulo, valor, negrita in [
            (62, "FLETE:", vr_flete, False), (65, "MANEJO:", vr_manejo, False),
            (68, "OTROS:", 0, False), (71, "TOTAL:", vr_total, True),
        ]:
            l.fuente(7, negrita=True)
            l.celda(6, y, 13, 3, titulo, relleno=_BLANCO)
            l.fuente(7, negrita=negrita)
            l.celda(20, y, 28, 3, numero(valor), alinear="R", relleno=_BLANCO)
        l.fuente(7, negrita=True)
        l.texto(7, 77, "Valor declarado ")
        l.texto(30, 77, numero(vr_declara))

        l.rect(49, 56, 48, 5)
        self._textos(l, True, [(51, 59, "UND:"), (65, 59, "PESO:"), (82, 59, "VOL:")])
        self._textos(l, False, [
            (58, 59, fmt_cantidad(g.unidades)), (73, 59, fmt_cantidad(g.peso_real)),
            (89, 59, fmt_cantidad(g.peso_volumen)),
        ])

        # ── Recibido ──────────────────────────────────────────────────────────
        l.fuente(5)
        for x, ancho, texto, color in [
            (49, 12, "Fecha Recib:", _NEGRO), (61, 15, "DD MM AAAA", _GRIS),
            (76, 8, "Hora:", _NEGRO), (84, 13, "HH: MM", _GRIS),
        ]:
            l.color_texto(*color)
            l.celda(x, 61, ancho, 4, texto)
        l.color_texto(*_NEGRO)
        l.rect(49, 61, 48, 18)
        l.linea(52, 75, 92, 75)
        l.fuente(7, negrita=True)
        l.texto(58, 78, "FIRMA DESTINATARIO")

        # ── Comentarios y pie ─────────────────────────────────────────────────
        l.rect(5, 79, 92, 12)
        l.fuente(8, negrita=True)
        l.multicelda(5, 80, 92, 3, g.comentario[:250], max_lineas=3)

        l.fuente(6)
        if not g.contenido_verificado:
            l.texto(5, 93, "Sin verificar contenido")
        l.texto(50, 93, f"Usuario: {g.usuario}")
        l.fuente(5)
        l.texto(5, 95, g.tipo_mensaje_formato)
        l.texto(60, 97, f"{ahora_local():%Y-%m-%d %H:%M:%S} [Semantica ERP | Logistica]")

    @staticmethod
    def _textos(l: Lienzo, negrita: bool, textos: list[tuple]) -> None:
        """Textos de 7 pt en (x, y); un cuarto valor opcional es el ancho máximo en mm."""
        l.fuente(7, negrita=negrita)
        for x, y, texto, *ancho in textos:
            l.texto(x, y, l.ajustar(texto, ancho[0]) if ancho else texto)

    @staticmethod
    def _valores(g: GuiaImpresion) -> tuple[float, float, float, float]:
        """Flete, manejo, total y declarado con las reglas de Guia2."""
        vr_flete, vr_manejo, vr_declara = g.vr_flete, g.vr_manejo, g.vr_declara
        vr_total = vr_flete + vr_manejo
        if not g.factura and g.codigo_pago == "COR":
            if g.tercero_ocultar_valores:
                vr_flete = vr_manejo = vr_total = 0
            if g.tercero_ocultar_declarado:
                vr_declara = 0
        return vr_flete, vr_manejo, vr_total, vr_declara

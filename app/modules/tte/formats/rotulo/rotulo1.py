"""
Rótulo formato 1 — etiqueta 100×100 mm, una por unidad.
Réplica de holmio `src/Formato/Transporte/Rotulo1.php`; las coordenadas son las mismas (mm).
"""
from reportlab.lib.units import mm

from app.core.pdf_lienzo import FormatoPdf, Lienzo
from app.core.utils import ahora_local, fmt_cantidad
from app.modules.tte.formats.datos import EmpresaImpresion, GuiaImpresion, numero
from app.modules.tte.formats.rotulo import piezas, registro

_BORDE_DERECHO = 96  # mm; hasta donde llegan las líneas divisorias
_CAJA_ZONA = 80      # mm; los textos a la izquierda de la caja de zona no deben pisarla


@registro.registrar
class Rotulo1(FormatoPdf):
    codigo = 1
    nombre = "Etiqueta 100×100 mm"
    tamano = (100 * mm, 100 * mm)

    def paginas(self, guia: GuiaImpresion) -> int:
        return piezas(guia.unidades)

    def dibujar(self, l: Lienzo, g: GuiaImpresion, e: EmpresaImpresion, pagina: int) -> None:
        l.codigo_barras(f"{g.codigo}U{pagina}", 5, 86, 50, 8, tipo="Code128")
        l.qr(g.codigo, 70, 10, 20)

        # ── Encabezado ────────────────────────────────────────────────────────
        l.fuente(10, negrita=True)
        l.celda(5, 5, 85, 5, e.nombre[:40], alinear="C")
        l.celda(5, 10, 80, 5, f"NIT {e.nit}-{e.digito_verificacion}", alinear="C")
        l.celda(5, 15, 80, 5, f"TELEFONO: {e.telefono}", alinear="C")
        l.fuente(12, negrita=True)
        l.texto(5, 25, f"GUIA No. {g.codigo}")
        l.fuente(9, negrita=True)
        l.texto(5, 30, g.tipo_nombre)

        # ── Remitente ─────────────────────────────────────────────────────────
        self._rotulos(l, [(5, 34, "FECHA:"), (37, 34, "DOC-CLIENTE:"), (5, 38, "REMITENTE:"),
                          (5, 42, "DIRECCION:"), (5, 46, "ORIGEN:"), (5, 50, "EMPAQUE:"),
                          (5, 54, "PESO:"), (30, 54, "VOLUMEN:"), (60, 54, "RELACION:")])
        fecha = g.fecha_ingreso.strftime("%Y-%m-%d %H:%M") if g.fecha_ingreso else ""
        self._valores(l, _BORDE_DERECHO, [
            (15, 34, fecha), (55, 34, g.documento_cliente[:30]), (21, 38, g.remitente_nombre),
            (21, 42, g.remitente_direccion), (21, 46, g.ciudad_origen_nombre), (21, 50, "VARIOS"),
            (15, 54, fmt_cantidad(g.peso_real)), (45, 54, fmt_cantidad(g.peso_volumen)),
            (74, 54, g.relacion_cliente),
        ])
        l.linea(5, 56, _BORDE_DERECHO, 56)

        # ── Destinatario ──────────────────────────────────────────────────────
        self._rotulos(l, [(5, 60, "DESTINATARIO:"), (5, 64, "DIRECCION:"), (5, 68, "DESTINO:"),
                          (5, 72, "TELEFONO:"), (5, 76, "COMENTARIOS:")])
        self._valores(l, _BORDE_DERECHO, [(25, 60, g.destinatario_nombre)])
        self._valores(l, _CAJA_ZONA - 1, [
            (20, 64, g.destinatario_direccion), (20, 68, g.ciudad_destino_nombre),
            (20, 72, g.destinatario_telefono), (25, 76, g.comentario),
        ])

        l.fuente(7, negrita=True)
        l.rect(_CAJA_ZONA, 65, 16, 4)
        l.rect(_CAJA_ZONA, 69, 16, 9)
        l.texto(85, 68, "ZONA")
        l.fuente(16, negrita=True)
        l.texto(81, 75, l.ajustar(g.franja, 18))  # como en holmio, puede salir de la caja
        l.linea(5, 78, _BORDE_DERECHO, 78)

        # ── Control ───────────────────────────────────────────────────────────
        self._rotulos(l, [(5, 82, "OPERACION INGRESO:"), (5, 85, "USUARIO:")])
        self._valores(l, 54, [(35, 82, g.operacion_ingreso), (20, 85, g.usuario)])
        if g.vr_cobro_entrega > 0:
            l.fuente(7, negrita=True)
            l.texto(55, 82, "COBRO ENTREGA:")
            l.fuente(8)
            l.texto(80, 82, numero(g.vr_cobro_entrega))

        l.fuente(14, negrita=True)
        l.texto(58, 90, f"PIEZA {pagina} / {fmt_cantidad(g.unidades)}")
        l.fuente(5)
        l.texto(58, 93, f"{ahora_local():%Y-%m-%d %H:%M:%S} [Semantica ERP | Logistica]")

    @staticmethod
    def _rotulos(l: Lienzo, textos: list[tuple[float, float, str]]) -> None:
        l.fuente(7, negrita=True)
        for x, y, texto in textos:
            l.texto(x, y, texto)

    @staticmethod
    def _valores(l: Lienzo, limite: float, textos: list[tuple[float, float, str]]) -> None:
        """Valores en fuente normal, recortados para no pasar de `limite` (mm)."""
        l.fuente(7)
        for x, y, texto in textos:
            l.texto(x, y, l.ajustar(texto, limite - x))

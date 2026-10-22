"""
Guía formato 4 — A4 con 2 copias (EMPRESA / DESTINATARIO).
Réplica de holmio `src/Formato/Transporte/Guia4.php`; las coordenadas son las mismas (mm).
"""
from pathlib import Path

from reportlab.lib.pagesizes import A4

from app.core.pdf_lienzo import FormatoPdf, Lienzo, imagen_lector
from app.core.utils import fmt_cantidad
from app.modules.tte.formats.datos import EmpresaImpresion, GuiaImpresion, numero
from app.modules.tte.formats.guia import registro

_SUPERTRANSPORTE = Path(__file__).parents[4] / "static" / "img" / "supertransporte.png"

_BLANCO = (255, 255, 255)

# (y de referencia, etiqueta, y de la etiqueta)
_COPIAS = [(0, "EMPRESA", 120), (150, "DESTINATARIO", 270)]


@registro.registrar
class Guia4(FormatoPdf):
    codigo = 4
    nombre = "A4 con 2 copias (empresa, destinatario)"
    tamano = A4

    def __init__(self):
        self._supertransporte = imagen_lector(_SUPERTRANSPORTE)

    def dibujar(self, l: Lienzo, guia: GuiaImpresion, empresa: EmpresaImpresion, pagina: int) -> None:
        logo = imagen_lector(empresa.logo)
        for y, etiqueta, y_etiqueta in _COPIAS:
            self._copia(l, guia, empresa, y, logo)
            l.fuente(10, negrita=True)
            l.celda(75, y_etiqueta, 55, 4, etiqueta, alinear="C")

    def _copia(self, l: Lienzo, g: GuiaImpresion, e: EmpresaImpresion, y: float, logo) -> None:
        vr_flete, vr_manejo, vr_total, mensaje_contado = self._valores(g, e)

        # ── Imágenes y código de barras ───────────────────────────────────────
        l.imagen(logo, 10, y + 5, 50, 30)
        l.codigo_barras(g.codigo, 166, y + 20, 33, 10)
        l.imagen(self._supertransporte, 110, y + 16, 38, 18)

        l.fuente(10, negrita=True)
        if g.franja:
            l.rect(144, y + 10, 16, 4)
            l.rect(144, y + 14, 16, 9)
            l.texto(146, y + 13.5, "ZONA")
            l.texto(146, y + 20, g.franja)

        # ── Encabezado ────────────────────────────────────────────────────────
        l.celda(168, y + 10, 30, 4, g.tipo_nombre, alinear="C")
        l.celda(168, y + 15, 30, 4, g.codigo, alinear="C")
        l.fuente(9, negrita=True)
        l.texto(65, y + 15, e.nombre)
        l.texto(65, y + 20, f"{e.nit}-{e.digito_verificacion}")
        l.texto(65, y + 25, e.direccion)
        l.texto(65, y + 30, e.telefono)

        # ── Filas de datos: títulos en negrita arriba y valores debajo ─────────
        fecha = g.fecha_ingreso.strftime("%Y-%m-%d %H:%M") if g.fecha_ingreso else ""
        self._fila(l, y + 34, ("Fecha", "Origen", "Destino"),
                   (fecha, g.ciudad_origen_nombre, g.ciudad_destino_nombre))
        self._fila(l, y + 46, ("Remitente", "Dirección", "Telefono"),
                   (g.remitente_nombre, g.remitente_direccion[:30], g.remitente_telefono))
        self._fila(l, y + 58, ("Destinatario", "Dirección", "Telefono"),
                   (g.destinatario_nombre, g.destinatario_direccion[:30], g.destinatario_telefono))

        l.fuente(10, negrita=True)
        l.celda(10, y + 70, 190, 6, f"Tipo cobro:  {g.tipo_nombre}  {mensaje_contado}", borde="LTR", relleno=_BLANCO)
        l.fuente(10)
        documento = f"Documento:  {g.documento_cliente}" if g.documento_cliente else ""
        l.celda(10, y + 76, 190, 6, documento, borde="LBR", relleno=_BLANCO)

        # ── Cantidades y valores ──────────────────────────────────────────────
        l.fuente(10, negrita=True)
        for x, titulo in [(10, "Cant"), (25, "Peso"), (40, "Flete"), (55, "Manejo"), (70, "Total")]:
            l.celda(x, y + 82, 15, 6, titulo, borde=1, relleno=_BLANCO)
        l.celda(85, y + 82, 115, 6, "Devolver firmado y sellado", borde=1, alinear="C", relleno=_BLANCO)

        valores = [fmt_cantidad(g.unidades), fmt_cantidad(g.peso_facturado), numero(vr_flete), numero(vr_manejo), numero(vr_total)]
        for i, (x, valor) in enumerate(zip((10, 25, 40, 55, 70), valores)):
            l.fuente(8, negrita=i == 4)
            l.celda(x, y + 88, 15, 6, valor, borde="LR", relleno=_BLANCO)
            l.celda(x, y + 94, 15, 6, "", borde="LR", relleno=_BLANCO)
        l.fuente(10, negrita=True)
        l.celda(85, y + 88, 115, 6, "Nombre", borde="LTR", relleno=_BLANCO)
        l.celda(85, y + 94, 115, 6, "CC - NIT", borde="LBR", relleno=_BLANCO)

        # ── Observaciones ─────────────────────────────────────────────────────
        l.celda(10, y + 100, 190, 6, "Observaciones:", relleno=_BLANCO)
        l.rect(10, y + 100, 190, 18)
        l.multicelda(10, y + 106, 190, 4, g.comentario[:310], max_lineas=3)

    @staticmethod
    def _fila(l: Lienzo, y: float, titulos: tuple[str, str, str], valores: tuple[str, str, str]) -> None:
        columnas = [(10, 70), (80, 60), (140, 60)]
        l.fuente(10, negrita=True)
        for (x, ancho), titulo in zip(columnas, titulos):
            l.celda(x, y, ancho, 6, titulo, borde="LTR", relleno=_BLANCO)
        l.fuente(10)
        for (x, ancho), valor in zip(columnas, valores):
            # Como en holmio, un valor largo queda tapado por el fondo blanco de la celda siguiente
            l.celda(x, y + 6, ancho, 6, valor, borde="LBR", relleno=_BLANCO)

    @staticmethod
    def _valores(g: GuiaImpresion, e: EmpresaImpresion) -> tuple[float, float, float, str]:
        """Flete, manejo, total y mensaje de contado con las reglas de Guia4."""
        vr_flete, vr_manejo = g.vr_flete, g.vr_manejo
        vr_total = g.vr_flete + g.vr_manejo
        if not g.factura and (g.tercero_ocultar_valores or (e.ocultar_valores_formato_corriente and g.codigo_pago == "COR")):
            vr_flete = vr_manejo = vr_total = 0
        if g.codigo_pago == "CON":
            return vr_flete, vr_manejo, 0, "CANCELADO"
        return vr_flete, vr_manejo, vr_total, ""

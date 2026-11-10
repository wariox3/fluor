"""
Formato PDF de la visita.

Port de `App\\Formato\\Crm\\Visita` de holmio: encabezado de la empresa, datos de la visita,
tabla de reportes, tabla de compromisos, línea de firma, "Página X de Y" y marca de agua
"ANULADO" o "SIN APROBAR" según el estado de la visita. A diferencia de holmio, también
imprime el motivo y el asesor, y el nombre de cada compromiso junto a su detalle.
"""

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.pdf_header import encabezado_pdf

# ── Página ─────────────────────────────────────────────────────────────────────
_MARGIN = 1.5 * cm
_W = letter[0] - 2 * _MARGIN

# ── Colores ────────────────────────────────────────────────────────────────────
_AZUL = colors.HexColor("#1a3c5e")
_GRIS_BG = colors.HexColor("#dce6f0")
_BORDE = colors.HexColor("#999999")
_MARCA_AGUA = colors.HexColor("#ffdcdc")

# ── Estilos ────────────────────────────────────────────────────────────────────
_S = {
    "lbl": ParagraphStyle("lbl", fontSize=7, fontName="Helvetica-Bold"),
    "val": ParagraphStyle("val", fontSize=7, leading=9),
    "th": ParagraphStyle("th", fontSize=7, fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_CENTER),
    "seccion": ParagraphStyle("seccion", fontSize=8, fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_CENTER),
    "td": ParagraphStyle("td", fontSize=7, leading=9),
    "vacio": ParagraphStyle("vacio", fontSize=7, textColor=colors.grey, alignment=TA_CENTER),
}

# Anchos de las tablas de reportes y compromisos: ID | FECHA | TEXTO
_ANCHOS_DETALLE = [1.2 * cm, 2.2 * cm, _W - 3.4 * cm]


def _p(texto, estilo="val") -> Paragraph:
    """Párrafo con el texto escapado; respeta los saltos de línea que se escriben en holmio."""
    contenido = escape(str(texto)) if texto is not None else ""
    return Paragraph(contenido.replace("\r\n", "\n").replace("\n", "<br/>"), _S[estilo])


def _fecha(valor) -> str:
    return valor.strftime("%Y-%m-%d") if valor else ""


def _estilo_tabla() -> TableStyle:
    return TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.3, _BORDE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ])


def _datos_visita(visita) -> Table:
    """Grid etiqueta | valor | etiqueta | valor, con el comentario a todo el ancho."""
    L = lambda t: _p(t, "lbl")
    V = lambda t: _p(t, "val")

    filas = [
        [L("NÚMERO:"), V(visita.codigo_visita_pk), L("FECHA:"), V(_fecha(visita.fecha))],
        [L("CLIENTE:"), V(visita.tercero_nombre_corto or ""), L("TIPO:"), V(visita.visita_tipo_nombre or "")],
        [L("MOTIVO:"), V(visita.visita_motivo_nombre or ""), L("ASESOR:"), V(visita.asesor_nombre or "")],
        [L("COMENTARIO:"), V(visita.comentarios or ""), V(""), V("")],
    ]
    tabla = Table(filas, colWidths=[2.4 * cm, _W / 2 - 2.4 * cm, 2.4 * cm, _W / 2 - 2.4 * cm])
    estilo = _estilo_tabla()
    estilo.add("BACKGROUND", (0, 0), (0, -1), _GRIS_BG)
    estilo.add("BACKGROUND", (2, 0), (2, 2), _GRIS_BG)
    estilo.add("SPAN", (1, 3), (3, 3))
    estilo.add("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    tabla.setStyle(estilo)
    return tabla


def _tabla_detalle(titulo: str, encabezado_texto: str, filas: list[list], vacio: str) -> Table:
    """Tabla con una barra de título, encabezados ID | FECHA | <texto> y sus filas."""
    datos = [
        [_p(titulo, "seccion"), "", ""],
        [_p("ID", "th"), _p("FECHA", "th"), _p(encabezado_texto, "th")],
    ]
    datos += filas or [[_p(vacio, "vacio"), "", ""]]

    tabla = Table(datos, colWidths=_ANCHOS_DETALLE, repeatRows=2)
    estilo = _estilo_tabla()
    estilo.add("SPAN", (0, 0), (-1, 0))
    estilo.add("BACKGROUND", (0, 0), (-1, 0), _AZUL)
    estilo.add("BACKGROUND", (0, 1), (-1, 1), _AZUL)
    if not filas:
        estilo.add("SPAN", (0, 2), (-1, 2))
    tabla.setStyle(estilo)
    return tabla


def _detalle_compromiso(compromiso) -> str:
    """Holmio solo imprime el detalle; se antepone el nombre para que el compromiso se entienda."""
    partes = [p for p in (compromiso.nombre, compromiso.detalle) if p]
    return ": ".join(partes)


class _CanvasNumerado(rl_canvas.Canvas):
    """
    Canvas que, al terminar, dibuja en cada página la firma y "Página X de Y", que necesita
    el total de páginas y este solo se conoce al final.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._paginas = []

    def showPage(self):
        self._paginas.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._paginas)
        for pagina in self._paginas:
            self.__dict__.update(pagina)
            self._pie(total)
            super().showPage()
        super().save()

    def _pie(self, total: int):
        ancho, _ = letter
        self.setFont("Helvetica-Bold", 8)
        self.line(_MARGIN, 2.3 * cm, _MARGIN + 7 * cm, 2.3 * cm)
        self.drawString(_MARGIN, 1.9 * cm, "FIRMA")
        self.setFont("Helvetica", 8)
        self.drawRightString(ancho - _MARGIN, 1.0 * cm, f"Página {self._pageNumber} de {total}")


def _dibujar_marca_agua(texto: str | None):
    """Se dibuja al iniciar cada página, así queda detrás del contenido como en holmio."""

    def dibujar(canvas, _doc):
        if not texto:
            return
        canvas.saveState()
        canvas.setFont("Helvetica", 40)
        canvas.setFillColor(_MARCA_AGUA)
        canvas.translate(letter[0] / 2, 11 * cm)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, texto)
        canvas.restoreState()

    return dibujar


def _marca_agua(visita) -> str | None:
    """Igual que holmio: la visita anulada o sin aprobar se marca en todas sus páginas."""
    if visita.estado_anulado:
        return "ANULADO"
    if not visita.estado_aprobado:
        return "SIN APROBAR"
    return None


def generar(visita, db) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=_MARGIN,
        rightMargin=_MARGIN,
        topMargin=_MARGIN,
        # Deja espacio para la firma y la numeración del pie
        bottomMargin=3 * cm,
        title=f"Visita {visita.codigo_visita_pk}",
    )

    story = encabezado_pdf(titulo="VISITA", db=db, ancho_util=_W)
    story.append(_datos_visita(visita))
    story.append(Spacer(1, 0.4 * cm))

    reportes = [
        [_p(r.codigo_visita_reporte_pk, "td"), _p(_fecha(r.fecha), "td"), _p(r.reporte or "", "td")]
        for r in visita.reportes
    ]
    story.append(_tabla_detalle("REPORTES", "REPORTE", reportes, "Sin reportes"))
    story.append(Spacer(1, 0.4 * cm))

    compromisos = [
        [_p(c.codigo_visita_compromiso_pk, "td"), _p(_fecha(c.fecha), "td"), _p(_detalle_compromiso(c), "td")]
        for c in visita.compromisos
    ]
    story.append(_tabla_detalle("COMPROMISOS", "DETALLE", compromisos, "Sin compromisos"))

    marca_agua = _dibujar_marca_agua(_marca_agua(visita))
    doc.build(story, onFirstPage=marca_agua, onLaterPages=marca_agua, canvasmaker=_CanvasNumerado)
    return buffer.getvalue()

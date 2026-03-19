from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

PAGE_PORTRAIT = letter
PAGE_LANDSCAPE = landscape(letter)

# Paleta corporativa
COLOR_PRIMARY = colors.HexColor("#1a3c5e")
COLOR_HEADER_BG = colors.HexColor("#1a3c5e")
COLOR_HEADER_FG = colors.white
COLOR_ROW_ALT = colors.HexColor("#f0f4f8")
COLOR_BORDER = colors.HexColor("#c0cfe0")

_styles = getSampleStyleSheet()

STYLE_TITLE = ParagraphStyle(
    "titulo",
    parent=_styles["Title"],
    fontSize=14,
    textColor=COLOR_PRIMARY,
    spaceAfter=4,
)
STYLE_SUBTITLE = ParagraphStyle(
    "subtitulo",
    parent=_styles["Normal"],
    fontSize=9,
    textColor=colors.HexColor("#555555"),
    spaceAfter=2,
)
STYLE_CELL = ParagraphStyle(
    "celda",
    parent=_styles["Normal"],
    fontSize=8,
    leading=10,
)
STYLE_CELL_RIGHT = ParagraphStyle(
    "celda_right",
    parent=STYLE_CELL,
    alignment=TA_RIGHT,
)


def tabla_style(num_cols: int, col_dinero: list[int] | None = None) -> TableStyle:
    """Estilo base para tablas. col_dinero: índices de columnas con alineación derecha."""
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), COLOR_HEADER_FG),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_ROW_ALT]),
        ("GRID", (0, 0), (-1, -1), 0.4, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    if col_dinero:
        for col in col_dinero:
            cmds.append(("ALIGN", (col, 0), (col, -1), "RIGHT"))
    return TableStyle(cmds)


def build_pdf(
    titulo: str,
    subtitulo: str,
    headers: list[str],
    rows: list[list],
    col_widths: list[float],
    col_dinero: list[int] | None = None,
    landscape_mode: bool = False,
) -> bytes:
    """Genera un PDF y retorna los bytes."""
    buffer = BytesIO()
    pagesize = PAGE_LANDSCAPE if landscape_mode else PAGE_PORTRAIT
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    story = [
        Paragraph(titulo, STYLE_TITLE),
        Paragraph(subtitulo, STYLE_SUBTITLE),
        Spacer(1, 0.4 * cm),
    ]

    header_row = [Paragraph(h, ParagraphStyle("h", parent=STYLE_CELL, textColor=colors.white, fontName="Helvetica-Bold", fontSize=8)) for h in headers]
    table_data = [header_row] + rows

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(tabla_style(len(headers), col_dinero))
    story.append(table)

    doc.build(story)
    return buffer.getvalue()

"""
Encabezado genérico para formatos PDF del ERP.

Uso:
    from app.core.pdf_header import encabezado_pdf

    story = []
    story += encabezado_pdf(
        titulo="COMPROBANTE DE PAGO DE NÓMINA",
        config=config,          # row de gen_configuracion (puede ser None)
        gen_imagen=gen_imagen,  # row de gen_imagen con PK='LOGO' (puede ser None)
    )
    # ... resto del story
"""

from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, Spacer, Table, TableStyle

# ── Constantes de layout ────────────────────────────────────────────────────────
_LOGO_W   = 3.0 * cm
_LOGO_H   = 3.0 * cm
_BORDE    = colors.HexColor("#999999")

# ── Estilos propios del encabezado ──────────────────────────────────────────────
_TS      = ParagraphStyle("hdr_ts",      fontSize=7, textColor=colors.grey, alignment=TA_RIGHT)
_TITLE   = ParagraphStyle("hdr_title",   fontSize=11, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=2)
_DEPT    = ParagraphStyle("hdr_dept",    fontSize=9,  fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=2)
_CO_INFO = ParagraphStyle("hdr_co_info", fontSize=8,  leading=13)


def _blob_to_bytes(blob) -> bytes | None:
    if blob is None:
        return None
    if isinstance(blob, (bytes, bytearray)):
        return blob
    if isinstance(blob, memoryview):
        return bytes(blob)
    try:
        return blob.read()
    except Exception:
        return None


def _logo_flowable(gen_imagen) -> Image | Table:
    """Devuelve un Image con el logo o un recuadro vacío si no hay imagen."""
    if gen_imagen:
        data = _blob_to_bytes(gen_imagen.imagen)
        if data:
            try:
                img = Image(BytesIO(data), width=_LOGO_W, height=_LOGO_H)
                img.hAlign = "CENTER"
                return img
            except Exception:
                pass
    # Recuadro vacío de respaldo
    box = Table([[""]], colWidths=[_LOGO_W], rowHeights=[_LOGO_H])
    box.setStyle(TableStyle([
        ("BOX",    (0, 0), (-1, -1), 0.5, _BORDE),
        ("ALIGN",  (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return box


def encabezado_pdf(
    titulo: str,
    config=None,
    gen_imagen=None,
    ancho_util: float | None = None,
    departamento: str | None = None,
) -> list:
    """
    Construye el encabezado estándar y devuelve una lista de flowables.

    Parámetros
    ----------
    titulo        : Título principal del documento (centrado, negrita).
    config        : Row de gen_configuracion con nombre, nit, digito_verificacion,
                    telefono, direccion, correo. Puede ser None (usa datos demo).
    gen_imagen    : Row de gen_imagen (PK='LOGO'). Puede ser None.
    ancho_util    : Ancho disponible en puntos. Si None se calcula desde letter
                    con márgenes de 1.5 cm.
    departamento  : Línea opcional encima del título (ej. "DEPARTAMENTO DE TALENTO HUMANO").
    """
    from reportlab.lib.pagesizes import letter

    if ancho_util is None:
        ancho_util = letter[0] - 2 * (1.5 * cm)

    # ── Datos empresa ───────────────────────────────────────────────────────────
    nombre    = getattr(config, "nombre",            "EMPRESA DEMO S.A.S") if config else "EMPRESA DEMO S.A.S"
    nit_raw   = getattr(config, "nit",               "900000000")          if config else "900000000"
    dv        = getattr(config, "digito_verificacion", "0")                if config else "0"
    direccion = getattr(config, "direccion",          "")                  if config else ""
    telefono  = getattr(config, "telefono",           "")                  if config else ""
    correo    = getattr(config, "correo",             "")                  if config else ""
    nit       = f"{nit_raw}-{dv}"

    flowables = []

    # ── Timestamp ───────────────────────────────────────────────────────────────
    flowables.append(Paragraph(
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [Semantica | ERP]",
        _TS,
    ))

    # ── Logo + datos empresa ────────────────────────────────────────────────────
    info_lines = (
        f"<b>EMPRESA:</b> {nombre}<br/>"
        f"<b>NIT:</b> {nit}<br/>"
        f"<b>DIRECCIÓN:</b> {direccion}<br/>"
        f"<b>TELÉFONO:</b> {telefono}"
        + (f"<br/><b>CORREO:</b> {correo}" if correo else "")
    )
    header_row = Table(
        [[_logo_flowable(gen_imagen), Paragraph(info_lines, _CO_INFO)]],
        colWidths=[_LOGO_W + 0.3 * cm, ancho_util - _LOGO_W - 0.3 * cm],
    )
    header_row.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (1, 0), (1, 0),   8),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    flowables.append(header_row)
    flowables.append(Spacer(1, 0.3 * cm))

    # ── Departamento (opcional) ─────────────────────────────────────────────────
    if departamento:
        flowables.append(Paragraph(departamento.upper(), _DEPT))

    # ── Título ──────────────────────────────────────────────────────────────────
    flowables.append(Paragraph(titulo.upper(), _TITLE))
    flowables.append(Spacer(1, 0.2 * cm))

    return flowables

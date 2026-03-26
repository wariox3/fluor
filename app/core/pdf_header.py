"""
Encabezado genérico para formatos PDF del ERP.

Uso (pasando sesión de BD — recomendado):
    from app.core.pdf_header import encabezado_pdf

    story  = []
    story += encabezado_pdf(titulo="COMPROBANTE DE PAGO DE NÓMINA", db=db)

Uso alternativo (pasando objetos ya consultados):
    story += encabezado_pdf(titulo="...", config=config, gen_imagen=gen_imagen)
"""

from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, Spacer, Table, TableStyle

# ── Constantes de layout ────────────────────────────────────────────────────────
_LOGO_W = 3.0 * cm
_LOGO_H = 3.0 * cm
_BORDE  = colors.HexColor("#999999")

# ── Estilos propios del encabezado ──────────────────────────────────────────────
_TS      = ParagraphStyle("hdr_ts",      fontSize=7,  textColor=colors.grey, alignment=TA_RIGHT)
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
    if gen_imagen:
        data = _blob_to_bytes(gen_imagen.imagen)
        if data:
            try:
                img = Image(BytesIO(data), width=_LOGO_W, height=_LOGO_H)
                img.hAlign = "CENTER"
                return img
            except Exception:
                pass
    box = Table([[""]], colWidths=[_LOGO_W], rowHeights=[_LOGO_H])
    box.setStyle(TableStyle([
        ("BOX",    (0, 0), (-1, -1), 0.5, _BORDE),
        ("ALIGN",  (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return box


def _consultar_datos(db):
    """Consulta config e imagen desde la BD. Retorna (config, gen_imagen)."""
    from app.modules.gen.models.configuracion import Configuracion
    from app.modules.gen.models.imagen import Imagen

    config = db.query(Configuracion).with_entities(
        Configuracion.nombre,
        Configuracion.nit,
        Configuracion.digito_verificacion,
        Configuracion.telefono,
        Configuracion.direccion,
        Configuracion.correo,
    ).first()
    gen_imagen = db.query(Imagen).filter(Imagen.codigo_imagen_pk == "LOGO").first()
    return config, gen_imagen


def encabezado_pdf(
    titulo: str,
    db=None,
    config=None,
    gen_imagen=None,
    ancho_util: float | None = None,
    departamento: str | None = None,
) -> list:
    """
    Construye el encabezado estándar y devuelve una lista de flowables.

    Parámetros
    ----------
    titulo       : Título principal del documento.
    db           : Sesión SQLAlchemy. Si se pasa, consulta config e imagen automáticamente.
    config       : Row de gen_configuracion (usado solo si db es None).
    gen_imagen   : Row de gen_imagen PK='LOGO' (usado solo si db es None).
    ancho_util   : Ancho disponible en puntos. None = letter con márgenes 1.5 cm.
    departamento : Línea opcional sobre el título.
    """
    from reportlab.lib.pagesizes import letter

    if db is not None:
        config, gen_imagen = _consultar_datos(db)

    if ancho_util is None:
        ancho_util = letter[0] - 2 * (1.5 * cm)

    nombre    = getattr(config, "nombre",             "EMPRESA DEMO S.A.S") if config else "EMPRESA DEMO S.A.S"
    nit_raw   = getattr(config, "nit",                "900000000")          if config else "900000000"
    dv        = getattr(config, "digito_verificacion", "0")                 if config else "0"
    direccion = getattr(config, "direccion",           "")                  if config else ""
    telefono  = getattr(config, "telefono",            "")                  if config else ""
    correo    = getattr(config, "correo",              "")                  if config else ""
    nit       = f"{nit_raw}-{dv}"

    flowables = []

    flowables.append(Paragraph(
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [Semantica | ERP]",
        _TS,
    ))

    if departamento:
        flowables.append(Paragraph(departamento.upper(), _DEPT))

    flowables.append(Paragraph(titulo.upper(), _TITLE))
    flowables.append(Spacer(1, 0.3 * cm))

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

    return flowables

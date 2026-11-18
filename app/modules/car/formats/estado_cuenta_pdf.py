"""
Estado de cuenta formal del cliente: carta con sus cuentas por cobrar pendientes.

Port de `App\\Formato\\EstadoCuentaFormal` de terbio (lo generaba terbio, no holmio): logo de la
empresa, ciudad y fecha, destinatario, asunto, saludo, tabla TIPO | NÚMERO | FECHA | VENCE | PLAZO |
VALOR con el total del saldo, y cierre con el teléfono de la empresa y la firma del departamento
de cartera.

Terbio ubicaba cada texto en una posición fija de la página, así que con muchas cuentas la tabla
pisaba el cierre; aquí el contenido fluye y continúa en otra página. Los datos de la empresa salen de
`gen_configuracion` y el logo de `gen_imagen` (`LOGO`), como en los demás formatos de fluor. El
párrafo opcional que terbio guardaba por empresa en su propia base (`texto`, tipo 1) no se migró.
"""

from dataclasses import dataclass
from datetime import date
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# ── Página: márgenes de terbio (30 mm a la izquierda, 20 mm a la derecha) ─────────
_MARGIN_IZQ = 30 * mm
_MARGIN_DER = 20 * mm
_W = letter[0] - _MARGIN_IZQ - _MARGIN_DER

# Logo arriba a la derecha, 40 x 40 mm, como terbio
_LOGO_X = 150 * mm
_LOGO_Y = 20 * mm
_LOGO_LADO = 40 * mm

_GRIS_TH = colors.Color(170 / 255, 170 / 255, 170 / 255)

_MESES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

_S = {
    "texto": ParagraphStyle("ec_texto", fontName="Helvetica", fontSize=10, leading=14),
    "negrita": ParagraphStyle("ec_negrita", fontName="Helvetica-Bold", fontSize=10, leading=14),
    "parrafo": ParagraphStyle("ec_parrafo", fontName="Helvetica", fontSize=10, leading=14, alignment=TA_JUSTIFY),
    "th": ParagraphStyle("ec_th", fontName="Helvetica-Bold", fontSize=7, leading=9, alignment=TA_CENTER),
    "td": ParagraphStyle("ec_td", fontName="Helvetica", fontSize=8.5, leading=10),
    "td_r": ParagraphStyle("ec_td_r", fontName="Helvetica", fontSize=8.5, leading=10, alignment=TA_RIGHT),
}

# Columnas de terbio: TIPO | NÚMERO | FECHA | VENCE | PLAZO | VALOR
_ANCHOS = [w * mm for w in (50, 20, 20, 20, 20, 20)]


@dataclass
class Empresa:
    nombre: str | None
    telefono: str | None
    ciudad: str | None
    logo: bytes | None


@dataclass
class Cliente:
    nombre_corto: str | None
    numero_identificacion: str | None


@dataclass
class CuentaPendiente:
    tipo: str | None
    numero_documento: str | None
    fecha: object
    fecha_vence: object
    plazo: int | None
    vr_saldo: float | None


def _p(texto, estilo: str) -> Paragraph:
    contenido = escape(str(texto)) if texto is not None else ""
    return Paragraph(contenido, _S[estilo])


def _fecha(valor) -> str:
    return valor.strftime("%Y-%m-%d") if valor else ""


def _dinero(valor) -> str:
    """Como `number_format` de terbio: sin decimales y con coma de miles."""
    return f"{round(valor or 0):,}"


def _fecha_carta(ciudad: str | None, hoy: date) -> str:
    """`Bogotá, 18 de noviembre de 2026`, como el `strftime` en español de terbio."""
    return f"{ciudad or ''}, {hoy.day} de {_MESES[hoy.month]} de {hoy.year}"


def _tabla_cuentas(cuentas: list[CuentaPendiente]) -> Table:
    datos = [[_p(t, "th") for t in ("TIPO", "NÚMERO", "FECHA", "VENCE", "PLAZO", "VALOR")]]
    for c in cuentas:
        datos.append([
            _p(c.tipo, "td"),
            _p(c.numero_documento, "td"),
            _p(_fecha(c.fecha), "td"),
            _p(_fecha(c.fecha_vence), "td"),
            _p(c.plazo, "td"),
            _p(_dinero(c.vr_saldo), "td_r"),
        ])
    total = sum(c.vr_saldo or 0 for c in cuentas)
    datos.append(["", "", "", "", _p("Total", "td"), _p(_dinero(total), "td_r")])

    ultima = len(datos) - 1
    tabla = Table(datos, colWidths=_ANCHOS, repeatRows=1, hAlign="LEFT")
    tabla.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, ultima - 1), 0.5, colors.black),
        # El total solo lleva borde en sus dos celdas, como terbio
        ("GRID", (4, ultima), (5, ultima), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), _GRIS_TH),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    return tabla


def _dibujar_logo(logo: bytes | None):
    def dibujar(canvas, _doc):
        if not logo:
            return
        try:
            imagen = ImageReader(BytesIO(logo))
        except Exception:
            # Como terbio: si el logo no se puede leer, la carta sale sin él
            return
        canvas.drawImage(
            imagen,
            _LOGO_X,
            letter[1] - _LOGO_Y - _LOGO_LADO,
            width=_LOGO_LADO,
            height=_LOGO_LADO,
            preserveAspectRatio=True,
            mask="auto",
        )

    return dibujar


def generar(empresa: Empresa, cliente: Cliente, cuentas: list[CuentaPendiente], hoy: date) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=_MARGIN_IZQ,
        rightMargin=_MARGIN_DER,
        # La fecha va a 35 mm del borde, a la altura del logo
        topMargin=30 * mm,
        bottomMargin=20 * mm,
        title="Estado de cuenta",
    )

    telefono = empresa.telefono or ""
    story = [
        _p(_fecha_carta(empresa.ciudad, hoy), "texto"),
        Spacer(1, 10 * mm),
        _p("Señores:", "negrita"),
        _p(cliente.nombre_corto, "negrita"),
        _p(f"NIT: {cliente.numero_identificacion or ''}", "negrita"),
        Spacer(1, 18 * mm),
        _p("ASUNTO: ESTADO DE CUENTA", "negrita"),
        Spacer(1, 8 * mm),
        _p("Cordial saludo:", "texto"),
        Spacer(1, 4 * mm),
        _p(
            "Con el fin de mejorar la comunicación con nuestros clientes y garantizar el cruce de "
            "información correspondiente a su cartera, nos permitimos detallar las facturas "
            "pendientes por cancelar a la fecha:",
            "parrafo",
        ),
        Spacer(1, 3 * mm),
        _tabla_cuentas(cuentas),
        Spacer(1, 12 * mm),
        # El cierre no se parte: la firma queda en la misma página que el último párrafo
        KeepTogether([
            _p(
                "En caso de tener alguna observación con la información anexada favor comunicarse a "
                f"nuestro departamento de cartera, tel: {telefono} para actualizar dicha información.",
                "parrafo",
            ),
            Spacer(1, 8 * mm),
            _p("Atentamente,", "texto"),
            Spacer(1, 6 * mm),
            _p(empresa.nombre, "negrita"),
            _p("Departamento de Cartera", "negrita"),
        ]),
    ]

    doc.build(story, onFirstPage=_dibujar_logo(empresa.logo))
    return buffer.getvalue()

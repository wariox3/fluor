"""
Guía formato 1 — A4 (210×297 mm), 3 copias por página (REMITENTE / EMPRESA / DESTINATARIO).
Coordenadas en mm, origen superior-izquierdo (igual que FPDF).
"""
from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing, Group
from reportlab.graphics import renderPDF
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics

PAGE_SIZE = A4
_W, _H = PAGE_SIZE

_STATIC_IMG = Path(__file__).parents[3] / "static" / "img"
_MINISTERIO_IMG = str(_STATIC_IMG / "ministerio_transporte_2024.png")

_Y_OFFSETS = [12, 108, 204]
_COPY_LABELS = ["REMITENTE", "EMPRESA", "DESTINATARIO"]
_LABEL_Y_OFFSET = 75  # mm relativo a cada y0, alineado con el bloque de texto legal


# ── Coordenadas ───────────────────────────────────────────────────────────────

def _y(y_mm: float) -> float:
    return _H - y_mm * mm


def _iy(y_mm: float, h_mm: float) -> float:
    return _H - (y_mm + h_mm) * mm


def _rect(c, x, y, w, h):
    c.rect(x * mm, _iy(y, h), w * mm, h * mm)


# ── Helpers de datos ──────────────────────────────────────────────────────────

def _safe(obj, *attrs, default: str = "") -> str:
    for attr in attrs:
        if obj is None:
            return default
        obj = getattr(obj, attr, None)
    return str(obj) if obj is not None else default


def _num(val) -> str:
    try:
        return f"{int(float(val or 0)):,}"
    except (TypeError, ValueError):
        return "0"


# ── Helpers de dibujo ─────────────────────────────────────────────────────────

def _bold(c, size):
    c.setFont("Helvetica-Bold", size)


def _regular(c, size):
    c.setFont("Helvetica", size)


def _qr(value: str, size_mm: float) -> Drawing:
    qr = QrCodeWidget(str(value))
    b = qr.getBounds()
    w, h = b[2] - b[0], b[3] - b[1]
    sz = size_mm * mm
    d = Drawing(sz, sz, transform=[sz / w, 0, 0, sz / h, 0, 0])
    d.add(qr)
    return d


def _barcode_scaled(value: str, w_mm: float, h_mm: float) -> Drawing:
    """Genera un Code128 y lo escala para que quepa exactamente en w_mm × h_mm."""
    bc = createBarcodeDrawing("Code128", value=str(value),
                               barHeight=h_mm * mm, barWidth=1.0, humanReadable=False)
    target_w = w_mm * mm
    sx = target_w / bc.width if bc.width else 1.0
    g = Group(bc)
    g.transform = (sx, 0, 0, 1, 0, 0)
    d = Drawing(target_w, h_mm * mm)
    d.add(g)
    return d


def _draw_paragraph(c, text, x_mm, y_mm, max_w_mm, font_name, size, leading_mm=2.2):
    """Word-wrap de texto dentro de max_w_mm; dibuja línea por línea hacia abajo."""
    max_w = max_w_mm * mm
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if pdfmetrics.stringWidth(candidate, font_name, size) <= max_w:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    c.setFont(font_name, size)
    for i, line in enumerate(lines):
        c.drawString(x_mm * mm, _y(y_mm + i * leading_mm), line)


def _logo_image(logo):
    if logo and logo.imagen:
        try:
            return ImageReader(BytesIO(bytes(logo.imagen)))
        except Exception:
            return None
    return None


# ── Dibuja una copia ──────────────────────────────────────────────────────────

def _draw_copy(c, guia, y0: float, config, logo_img):
    c.setLineWidth(0.4)

    # Logo empresa
    if logo_img:
        c.drawImage(logo_img, 6 * mm, _iy(y0 - 5, 16), 16 * mm, 16 * mm,
                    preserveAspectRatio=True, mask="auto")

    # Vigilado SuperTransporte
    try:
        c.drawImage(_MINISTERIO_IMG, 5 * mm, _iy(y0 + 71, 10), 28 * mm, 10 * mm,
                    preserveAspectRatio=True, mask="auto")
    except Exception:
        pass

    # QR
    renderPDF.draw(_qr(str(guia.codigo_guia_pk), 15), c, 66 * mm, _iy(y0 - 5, 15))

    # Código de barras (top-right) — ancho fijo 34 mm para no salir del borde
    renderPDF.draw(_barcode_scaled(guia.codigo_guia_pk, 34, 8), c, 166 * mm, _iy(y0 + 2, 8))

    # Marca de agua ANULADO
    if guia.estado_anulado:
        c.saveState()
        c.setFont("Helvetica-Bold", 55)
        c.setFillColorRGB(1, 0.86, 0.86)
        c.translate(97 * mm, _y(y0 + 40))
        c.rotate(45)
        c.drawCentredString(0, 0, "ANULADO")
        c.restoreState()

    # ── Encabezado empresa ────────────────────────────────────────────────────
    _bold(c, 8)
    tipo = _safe(guia.guia_tipo, "nombre").upper() if guia.guia_tipo else ""
    c.drawCentredString(183 * mm, _y(y0 - 3), tipo)
    _bold(c, 7)
    c.drawCentredString(181.5 * mm, _y(y0 + 1), str(guia.codigo_guia_pk))

    _bold(c, 10)
    c.drawString(87 * mm, _y(y0 - 2), _safe(config, "nombre")[:50])
    _regular(c, 8)
    c.drawString(87 * mm, _y(y0 + 2),
                 f"NIT {_safe(config, 'nit')}-{_safe(config, 'digito_verificacion')}")
    c.drawString(87 * mm, _y(y0 + 5),
                 f"{_safe(config, 'direccion')} TEL: {_safe(config, 'telefono')}"[:55])
    c.drawString(87 * mm, _y(y0 + 8.5), _safe(config, "correo")[:55])

    # ── ROW 1: Remitente | Origen | Destino | Doc Cliente | Forma Pago ─────────
    _rect(c, 5, y0 + 11, 83, 13)
    _bold(c, 6)
    c.drawString(5.5 * mm, _y(y0 + 14), "REMITENTE  IDENTIFICACIÓN  NOMBRE  DIRECCIÓN")
    _regular(c, 6)
    c.drawString(5.5 * mm, _y(y0 + 17.5), _safe(guia, "nombre_remitente")[:32])
    c.drawString(65 * mm, _y(y0 + 17.5),
                 f"NIT/CC {_safe(guia.tercero, 'numero_identificacion')}"[:20])
    c.drawString(5.5 * mm, _y(y0 + 21.5), _safe(guia, "direccion_remitente")[:30])
    c.drawString(42 * mm, _y(y0 + 21.5), _safe(guia, "telefono_remitente")[:15])

    _rect(c, 88, y0 + 11, 34, 13)
    _bold(c, 6)
    c.drawString(88.5 * mm, _y(y0 + 14), "POBLACIÓN ORIGEN")
    _regular(c, 6)
    c.drawString(88.5 * mm, _y(y0 + 17.5), _safe(guia, "codigo_ciudad_origen_fk"))
    c.drawString(88.5 * mm, _y(y0 + 21.5),
                 _safe(guia.ciudad_origen, "nombre")[:18] if guia.ciudad_origen else "")

    _rect(c, 122, y0 + 11, 35, 13)
    _bold(c, 6)
    c.drawString(122.5 * mm, _y(y0 + 14), "POBLACIÓN DESTINO")
    _regular(c, 6)
    c.drawString(122.5 * mm, _y(y0 + 17.5), _safe(guia, "codigo_ciudad_destino_fk"))
    c.drawString(122.5 * mm, _y(y0 + 21.5),
                 _safe(guia.ciudad_destino, "nombre")[:18] if guia.ciudad_destino else "")

    _rect(c, 157, y0 + 11, 28, 13)
    _bold(c, 6)
    c.drawCentredString(171 * mm, _y(y0 + 14), "DOC CLIENTE")
    _regular(c, 6)
    c.drawString(157.5 * mm, _y(y0 + 17.5), _safe(guia, "documento_cliente")[:16])

    _rect(c, 185, y0 + 11, 17, 13)
    _bold(c, 6)
    c.drawCentredString(193.5 * mm, _y(y0 + 14), "FORMA PAGO")
    _regular(c, 6)
    c.drawCentredString(193.5 * mm, _y(y0 + 17.5), _safe(guia, "codigo_pago_fk"))

    # ── ROW 2: Destinatario | Fechas | Relación+NúmFact | Zona+Servicio ────────
    _rect(c, 5, y0 + 24, 83, 14)
    _bold(c, 6)
    c.drawString(5.5 * mm, _y(y0 + 27), "DESTINATARIO  NOMBRE  DIRECCIÓN  TELÉFONO")
    _regular(c, 6)
    c.drawString(5.5 * mm, _y(y0 + 30.5), _safe(guia, "nombre_destinatario")[:32])
    c.drawString(65 * mm, _y(y0 + 30.5),
                 f"NIT/CC {_safe(guia, 'numero_identificacion_destinatario')}"[:20])
    c.drawString(5.5 * mm, _y(y0 + 35), _safe(guia, "direccion_destinatario")[:30])
    c.drawString(65 * mm, _y(y0 + 35), _safe(guia, "telefono_destinatario")[:12])

    _rect(c, 88, y0 + 24, 36, 14)
    _bold(c, 6)
    c.drawString(88.5 * mm, _y(y0 + 27), "FECHA ELABORACIÓN")
    _regular(c, 6)
    if guia.fecha_ingreso:
        c.drawString(89 * mm,  _y(y0 + 30.5), guia.fecha_ingreso.strftime("%d"))
        c.drawString(96 * mm,  _y(y0 + 30.5), guia.fecha_ingreso.strftime("%m"))
        c.drawString(105 * mm, _y(y0 + 30.5), guia.fecha_ingreso.strftime("%Y"))
    c.drawString(89 * mm,  _y(y0 + 35), "DD")
    c.drawString(96 * mm,  _y(y0 + 35), "MM")
    c.drawString(105 * mm, _y(y0 + 35), "AAAA")

    _rect(c, 124, y0 + 24, 27, 14)
    _bold(c, 6)
    c.drawString(124.5 * mm, _y(y0 + 27), "FECHA ENTREGA")
    _regular(c, 6)
    if guia.fecha_entrega:
        c.drawString(125 * mm, _y(y0 + 30.5), guia.fecha_entrega.strftime("%d"))
        c.drawString(129 * mm, _y(y0 + 30.5), guia.fecha_entrega.strftime("%m"))
        c.drawString(134 * mm, _y(y0 + 30.5), guia.fecha_entrega.strftime("%Y"))
    c.drawString(125 * mm, _y(y0 + 35), "DD")
    c.drawString(129 * mm, _y(y0 + 35), "MM")
    c.drawString(134 * mm, _y(y0 + 35), "AAAA")

    _rect(c, 151, y0 + 24, 34, 8)
    _bold(c, 6)
    c.drawCentredString(168 * mm, _y(y0 + 27), "RELACIÓN")
    _regular(c, 6)
    c.drawString(152 * mm, _y(y0 + 30.5), _safe(guia, "relacion_cliente")[:20])

    _rect(c, 185, y0 + 24, 17, 8)
    _bold(c, 6)
    c.drawCentredString(193.5 * mm, _y(y0 + 27), "ZONA")
    _regular(c, 6)
    c.drawCentredString(193.5 * mm, _y(y0 + 30.5), _safe(guia, "codigo_zona_fk"))

    _rect(c, 151, y0 + 32, 34, 10)
    _bold(c, 6)
    c.drawCentredString(168 * mm, _y(y0 + 35), "NÚMERO FACTURA")
    _regular(c, 6)
    c.drawCentredString(168 * mm, _y(y0 + 39),
                        str(guia.numero_factura) if guia.numero_factura else "")

    _rect(c, 185, y0 + 32, 17, 10)
    _bold(c, 6)
    c.drawCentredString(193.5 * mm, _y(y0 + 35), "SERVICIO")
    _regular(c, 6)
    c.drawCentredString(193.5 * mm, _y(y0 + 39),
                        _safe(guia.servicio, "nombre")[:10] if guia.servicio else "")

    # ── Declaración + encabezado novedades ────────────────────────────────────
    _rect(c, 5, y0 + 38, 83, 8)
    _bold(c, 6)
    c.drawString(5.5 * mm, _y(y0 + 40),
                 "EL REMITENTE DECLARA QUE ESTE DESPACHO CONTIENE UNICAMENTE")

    _rect(c, 88, y0 + 38, 63, 4)
    _bold(c, 6)
    c.drawCentredString(119.5 * mm, _y(y0 + 40.5), "NOVEDADES")

    # ── Columna de valores (x=5-28) ───────────────────────────────────────────
    vr_flete  = float(guia.vr_flete or 0)
    vr_manejo = float(guia.vr_manejo or 0)
    vr_reexp  = float(guia.vr_costo_reexpedicion or 0)
    vr_total  = vr_flete + vr_manejo + vr_reexp
    vr_recaudo = float(guia.vr_recaudo or 0)

    for lbl, y_box, h_box, val in [
        ("VALOR DECLARADO", y0 + 46, 5, _num(guia.vr_declara)),
        ("COSTO MANEJO",    y0 + 51, 5, _num(vr_manejo)),
        ("FLETE",           y0 + 56, 5, _num(vr_flete)),
        ("TOTAL",           y0 + 61, 5, _num(vr_total)),
        ("RECAUDO:",        y0 + 66, 5, _num(vr_recaudo)),
    ]:
        _rect(c, 5, y_box, 23, h_box)
        _bold(c, 4)
        c.drawString(5.5 * mm, _y(y_box + 1.5), lbl)
        _regular(c, 6)
        c.drawRightString(27.5 * mm, _y(y_box + h_box - 1), val)

    # ── Columnas centrales (x=28-58 y x=58-88) ───────────────────────────────
    prod = _safe(guia.producto, "nombre")[:14] if guia.producto else ""
    for lbl, y_box, h_box, x, val in [
        ("UNIDADES",     y0 + 46, 8, 28, _num(guia.unidades)),
        ("C.REEXP",      y0 + 54, 8, 28, _num(vr_reexp)),
        ("PESO COBRADO", y0 + 62, 9, 28, _num(guia.peso_facturado)),
        ("PESO REAL",    y0 + 46, 8, 58, _num(guia.peso_real)),
        ("PESO VOLUMEN", y0 + 54, 8, 58, _num(guia.peso_volumen)),
        ("PRODUCTO",     y0 + 62, 9, 58, prod),
    ]:
        _rect(c, x, y_box, 30, h_box)
        _bold(c, 6)
        c.drawCentredString((x + 15) * mm, _y(y_box + 2.5), lbl)
        _regular(c, 6)
        c.drawCentredString((x + 15) * mm, _y(y_box + h_box - 2), val)

    # ── Novedades opciones (x=88-151) ─────────────────────────────────────────
    _rect(c, 88, y0 + 42, 34, 12)   # columna etiquetas
    _rect(c, 122, y0 + 42, 29, 12)  # columna otros/checkboxes
    _bold(c, 4)
    c.drawString(130.5 * mm, _y(y0 + 43.5), "OTROS")
    for lbl, yi in [
        ("DIRECCIÓN ERRADA",              y0 + 42),
        ("DESTINATARIO NO RECIBE / NO ESTA", y0 + 45),
        ("DESTINATARIO DESCONOCIDO",      y0 + 48),
        ("OTROS",                         y0 + 51),
    ]:
        _rect(c, 122, yi, 8, 3)
        _bold(c, 4)
        c.drawString(88.5 * mm, _y(yi + 2), lbl)

    # ── Observaciones ─────────────────────────────────────────────────────────
    _rect(c, 88, y0 + 54, 63, 8)
    _bold(c, 4.5)
    obs = f"OBSERVACIONES: {_safe(guia, 'comentario')[:80]}"
    c.drawString(88.5 * mm, _y(y0 + 55.5), obs[:78])

    # ── Entregado por ─────────────────────────────────────────────────────────
    _rect(c, 151, y0 + 42, 51, 12)
    _bold(c, 6)
    c.drawString(153 * mm, _y(y0 + 44), "ENTREGADO POR")

    # ── Legalizado / Escaneada / Cartaporte ───────────────────────────────────
    _rect(c, 151, y0 + 54, 16, 8)
    _bold(c, 4)
    c.drawCentredString(159 * mm, _y(y0 + 56), "LEGALIZADO")

    _rect(c, 167, y0 + 54, 18, 8)
    c.drawCentredString(176 * mm, _y(y0 + 56), "ESCANEADA")

    _rect(c, 185, y0 + 54, 17, 8)
    c.drawCentredString(193.5 * mm, _y(y0 + 56), "CARTAPORTE:")

    # ── Firma remitente / destinatario ────────────────────────────────────────
    _rect(c, 88, y0 + 62, 63, 9)
    _bold(c, 6)
    c.drawCentredString(119.5 * mm, _y(y0 + 64.5),
                        "NOMBRE Y CÉDULA REMITENTE/DESTINATARIO")

    # ── Firma y cédula recibe ─────────────────────────────────────────────────
    _rect(c, 151, y0 + 62, 51, 9)
    _bold(c, 6)
    c.drawCentredString(176.5 * mm, _y(y0 + 64.5), "FIRMA Y CÉDULA RECIBE")

    # ── Texto legal ───────────────────────────────────────────────────────────
    _legal = (
        "El contrato de transporte se rige por los arts. 1008 al 1035 del C. de C. y respondemos "
        "unicamente hasta el valor informado. No devuelva mercancia sin exigir los documentos "
        "firmados. No se aceptan reclamaciones despues de 90 dias. "
        "OPE-03-D02 Res.322 Nov.4/2014 Mintransporte."
    )
    _draw_paragraph(c, _legal, 115, y0 + 73, 87, "Helvetica", 4, leading_mm=2.2)


# ── Función pública ───────────────────────────────────────────────────────────

def generar_pagina(c, guia, config, logo=None):
    """Dibuja las 3 copias de la guía en la página actual del canvas."""
    logo_img = _logo_image(logo)

    for i, y0 in enumerate(_Y_OFFSETS):
        _draw_copy(c, guia, y0, config, logo_img)
        _bold(c, 7)
        c.drawCentredString(102.5 * mm, _y(y0 + _LABEL_Y_OFFSET), _COPY_LABELS[i])

    # Separadores entre copias
    c.setDash(4, 3)
    c.line(5 * mm, _y(96),  202 * mm, _y(96))
    c.line(5 * mm, _y(192), 202 * mm, _y(192))
    c.setDash()

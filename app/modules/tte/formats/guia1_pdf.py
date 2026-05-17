"""
Guía formato 1 — A4 (210×297 mm), 4 copias por página apiladas.
Réplica del Guia1.php — formato horizontal compacto con logo, barcode Code39
y tabla de liquidación al final de cada copia.
Coordenadas en mm, origen superior-izquierdo (igual que FPDF).
"""
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing, Group
from reportlab.graphics import renderPDF
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics

PAGE_SIZE = A4
_W, _H = PAGE_SIZE

# y de referencia de cada copia (igual que $y en el PHP).
# El header va por encima (y-16 → y); el cuerpo va por debajo (y → y+48).
_Y_REFS = [20, 88, 156, 224]


# ── Coordenadas ───────────────────────────────────────────────────────────────

def _y(y_mm):  return _H - y_mm * mm
def _iy(y, h): return _H - (y + h) * mm


# ── Primitivas ────────────────────────────────────────────────────────────────

def _rect(c, x, y, w, h):
    c.rect(x * mm, _iy(y, h), w * mm, h * mm, fill=0, stroke=1)

def _bold(c, size):    c.setFont("Helvetica-Bold", size)
def _regular(c, size): c.setFont("Helvetica", size)


# ── Helpers de datos ──────────────────────────────────────────────────────────

def _safe(obj, *attrs, default=""):
    for attr in attrs:
        if obj is None: return default
        obj = getattr(obj, attr, None)
    return str(obj) if obj is not None else default

def _num(val):
    try:    return f"{int(float(val or 0)):,}"
    except: return "0"

def _logo_image(logo):
    if logo and logo.imagen:
        try: return ImageReader(BytesIO(bytes(logo.imagen)))
        except: return None
    return None

def _barcode_scaled(value, w_mm, h_mm):
    """Code39 escalado para que quepa exacto en w_mm × h_mm."""
    bc = createBarcodeDrawing("Standard39", value=str(value),
                               barHeight=h_mm * mm, barWidth=1.0,
                               humanReadable=False, checksum=0)
    target_w = w_mm * mm
    sx = target_w / bc.width if bc.width else 1.0
    g = Group(bc); g.transform = (sx, 0, 0, 1, 0, 0)
    d = Drawing(target_w, h_mm * mm); d.add(g)
    return d

def _wrap(text, max_w_mm, font, size):
    max_w = max_w_mm * mm
    words = str(text).split()
    lines, current = [], ""
    for w in words:
        test = f"{current} {w}".strip()
        if pdfmetrics.stringWidth(test, font, size) <= max_w:
            current = test
        else:
            if current: lines.append(current)
            current = w
    if current: lines.append(current)
    return lines


# ── Dibuja una copia ──────────────────────────────────────────────────────────

def _draw_copy(c, guia, y, config, logo_img):
    """y es el 'y de referencia' de la copia (igual semántica que el PHP)."""
    c.setLineWidth(0.3)

    # ── HEADER: logo + barcode + tracking + datos empresa ─────────────────────
    if logo_img:
        c.drawImage(logo_img, 10 * mm, _iy(y - 16, 15), 40 * mm, 15 * mm,
                    preserveAspectRatio=True, mask="auto")

    renderPDF.draw(_barcode_scaled(guia.codigo_guia_pk, 33, 10),
                   c, 165 * mm, _iy(y - 10, 10))

    _bold(c, 12)
    c.drawRightString(198 * mm, _y(y - 12), str(guia.codigo_guia_pk))

    _regular(c, 8)
    c.drawString(55 * mm, _y(y - 13), _safe(config, "nombre")[:60])
    c.drawString(55 * mm, _y(y - 9),
                 f"{_safe(config,'nit')}-{_safe(config,'digito_verificacion')}")
    c.drawString(55 * mm, _y(y - 5), _safe(config, "direccion")[:55])
    c.drawString(55 * mm, _y(y - 1), _safe(config, "telefono"))

    # ── Row 1: Fecha | Origen | Destino ───────────────────────────────────────
    _rect(c, 10,  y, 61, 6)
    _rect(c, 71,  y, 60, 6)
    _rect(c, 131, y, 67, 6)
    _bold(c, 8)
    c.drawString(11 * mm,  _y(y + 4), "Fecha:")
    c.drawString(72 * mm,  _y(y + 4), "Origen:")
    c.drawString(132 * mm, _y(y + 4), "Destino:")
    _regular(c, 8)
    fecha_str = guia.fecha_ingreso.strftime("%Y-%m-%d") if guia.fecha_ingreso else ""
    c.drawString(23 * mm,  _y(y + 4), fecha_str)
    orig = _safe(guia.ciudad_origen, "nombre")[:24] if guia.ciudad_origen else ""
    dest = _safe(guia.ciudad_destino, "nombre")[:24] if guia.ciudad_destino else ""
    c.drawString(85 * mm,  _y(y + 4), orig)
    c.drawString(152 * mm, _y(y + 4), dest)

    # ── Row 2: Remite | Direccion (tercero) | Tel (tercero) ───────────────────
    _rect(c, 10,  y + 6, 61, 6)
    _rect(c, 71,  y + 6, 90, 6)
    _rect(c, 161, y + 6, 37, 6)
    _bold(c, 8)
    c.drawString(11 * mm,  _y(y + 10), "Remite:")
    c.drawString(72 * mm,  _y(y + 10), "Direccion:")
    c.drawString(162 * mm, _y(y + 10), "Tel:")
    _regular(c, 8)
    c.drawString(23 * mm,  _y(y + 10), _safe(guia, "nombre_remitente")[:32])
    c.drawString(88 * mm,  _y(y + 10), _safe(guia.tercero, "direccion")[:45])
    c.drawString(170 * mm, _y(y + 10), _safe(guia.tercero, "telefono")[:12])

    # ── Row 3: Destinatario | Direccion | Tel ─────────────────────────────────
    _rect(c, 10,  y + 12, 61, 6)
    _rect(c, 71,  y + 12, 90, 6)
    _rect(c, 161, y + 12, 37, 6)
    _bold(c, 8)
    c.drawString(11 * mm,  _y(y + 16), "Destinatario:")
    c.drawString(72 * mm,  _y(y + 16), "Direccion:")
    c.drawString(162 * mm, _y(y + 16), "Tel:")
    _regular(c, 8)
    c.drawString(31 * mm,  _y(y + 16), _safe(guia, "nombre_destinatario")[:24])
    _regular(c, 7)
    c.drawString(88 * mm,  _y(y + 16), _safe(guia, "direccion_destinatario")[:60])
    _regular(c, 8)
    c.drawString(170 * mm, _y(y + 16), _safe(guia, "telefono_destinatario")[:12])

    # ── Row 4-5: Tipo cobro + Documento (izquierda) | Observaciones (derecha) ─
    _rect(c, 10, y + 18, 61, 12)
    _bold(c, 8)
    c.drawString(11 * mm, _y(y + 22), "Tipo cobro:")
    c.drawString(11 * mm, _y(y + 28), "Documento:")
    _regular(c, 8)
    tipo = _safe(guia.guia_tipo, "nombre")[:20] if guia.guia_tipo else ""
    c.drawString(31 * mm, _y(y + 22), tipo)
    c.drawString(31 * mm, _y(y + 28), _safe(guia, "documento_cliente")[:25])

    _rect(c, 71, y + 18, 127, 12)
    _bold(c, 7.8)
    coment = f"Observaciones: {_safe(guia, 'comentario')}"
    lines = _wrap(coment, 125, "Helvetica-Bold", 7.8)[:3]
    for k, line in enumerate(lines):
        c.drawString(72 * mm, _y(y + 22 + k * 3.5), line)

    # ── Row 6: Headers de tabla (Cant ... Declarado | DEVOLVER FIRMADO ...) ───
    _rect(c, 10, y + 30, 188, 6)
    _bold(c, 8)
    for label, x in [
        ("Cant",      11),
        ("Peso",      21),
        ("Vol",       33),
        ("Flete",     46),
        ("Manejo",    61),
        ("Cobro",     81),
        ("Declarado", 96),
        ("DEVOLVER FIRMADO Y SELLADO", 131),
    ]:
        c.drawString(x * mm, _y(y + 34), label)

    # ── Row 7-8: Values (izq) | NOMBRE / CC NIT (der) ─────────────────────────
    _rect(c, 10,  y + 36, 105, 12)
    _rect(c, 115, y + 36, 83, 12)

    _regular(c, 8)
    for val, x in [
        (_num(guia.unidades),         11),
        (_num(guia.peso_real),        21),
        (_num(guia.peso_volumen),     33),
        (_num(guia.vr_flete),         46),
        (_num(guia.vr_manejo),        61),
        (_num(guia.vr_cobro_entrega), 81),
        (_num(guia.vr_declara),       96),
    ]:
        c.drawString(x * mm, _y(y + 40), val)

    _bold(c, 8)
    c.drawString(116 * mm, _y(y + 40), "NOMBRE")
    c.drawString(116 * mm, _y(y + 46), "CC NIT.")
    c.drawString(165 * mm, _y(y + 46), "FECHA HORA")


# ── Función pública ───────────────────────────────────────────────────────────

def generar_pagina(c, guia, config, logo=None):
    """Dibuja 4 copias de la guía apiladas en una página A4."""
    logo_img = _logo_image(logo)
    for y_ref in _Y_REFS:
        _draw_copy(c, guia, y_ref, config, logo_img)

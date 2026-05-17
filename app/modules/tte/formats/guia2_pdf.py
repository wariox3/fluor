"""
Guía formato 2 — 100×100 mm, una copia por guía.
Réplica del Guia2.php — formato compacto pensado para impresoras de etiquetas.
Coordenadas en mm, origen superior-izquierdo (igual que FPDF).
"""
from io import BytesIO
from datetime import datetime

from reportlab.lib.units import mm
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics

PAGE_SIZE = (100 * mm, 100 * mm)
_W, _H = PAGE_SIZE


# ── Coordenadas ───────────────────────────────────────────────────────────────

def _y(y_mm): return _H - y_mm * mm
def _iy(y, h): return _H - (y + h) * mm


# ── Líneas y rectángulos ──────────────────────────────────────────────────────

def _rect(c, x, y, w, h):
    c.rect(x * mm, _iy(y, h), w * mm, h * mm, fill=0, stroke=1)

def _fill_rect(c, x, y, w, h, color):
    c.setFillColorRGB(*color)
    c.rect(x * mm, _iy(y, h), w * mm, h * mm, fill=1, stroke=1)
    c.setFillColorRGB(0, 0, 0)

def _line(c, x1, y1, x2, y2):
    c.line(x1 * mm, _y(y1), x2 * mm, _y(y2))


# ── Texto ─────────────────────────────────────────────────────────────────────

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

def _qr(value, size_mm):
    qr = QrCodeWidget(str(value))
    b = qr.getBounds()
    sz = size_mm * mm
    d = Drawing(sz, sz, transform=[sz/(b[2]-b[0]), 0, 0, sz/(b[3]-b[1]), 0, 0])
    d.add(qr)
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


# ── Dibuja una copia (toda la página 100×100) ────────────────────────────────

def _draw_copy(c, guia, config, logo_img):
    c.setLineWidth(0.3)

    # QR top-right (74, 6, 20×20)
    renderPDF.draw(_qr(str(guia.codigo_guia_pk), 20), c, 74 * mm, _iy(6, 20))

    # Nombre empresa
    _bold(c, 10)
    c.drawString(4 * mm, _y(10), _safe(config, "nombre")[:50])

    # NIT + sitio web
    _bold(c, 8)
    nit_line = f"NIT {_safe(config,'nit')}-{_safe(config,'digito_verificacion')}"
    sitio = _safe(config, "sitio_web")
    if sitio:
        nit_line += f"  {sitio}"
    c.drawString(4 * mm, _y(15), nit_line[:60])

    # Tipo guía
    _bold(c, 10)
    tipo = _safe(guia.guia_tipo, "nombre").upper() if guia.guia_tipo else ""
    c.drawString(4 * mm, _y(20), tipo)

    # ZONA (caja header + caja contenido)
    _rect(c, 55, 16, 16, 4)
    _rect(c, 55, 20, 16, 8)
    _bold(c, 7)
    c.drawString(58 * mm, _y(19), "ZONA")
    c.drawString(57 * mm, _y(26), _safe(guia, "franja"))

    # GUÍA No. + Fecha
    _bold(c, 10)
    c.drawString(4 * mm, _y(24), f"GUIA No. {guia.codigo_guia_pk}")
    fecha_str = guia.fecha_ingreso.strftime("%y-%m-%d %H:%M") if guia.fecha_ingreso else ""
    c.drawString(4 * mm, _y(28), f"FECHA: {fecha_str}")

    # Aviso "* DEVOLVER DOCUMENTO ADJUNTO ..."
    if guia.devolver_documento_cliente and (_safe(guia, "codigo_pago_fk") == "COR"):
        _bold(c, 6.5)
        c.drawString(13 * mm, _y(34), "* DEVOLVER DOCUMENTO ADJUNTO FIRMADO Y SELLADO *")

    # ── Origen / Destino ──────────────────────────────────────────────────────
    _rect(c, 5,  31, 12, 5)
    _rect(c, 17, 31, 33, 5)
    _rect(c, 50, 31, 13, 5)
    _rect(c, 63, 31, 34, 5)
    _bold(c, 7)
    c.drawString(6 * mm,  _y(34.5), "ORIGEN:")
    c.drawString(51 * mm, _y(34.5), "DESTINO:")
    _regular(c, 7)
    orig = _safe(guia.ciudad_origen, "nombre")[:22] if guia.ciudad_origen else ""
    dest = _safe(guia.ciudad_destino, "nombre")[:22] if guia.ciudad_destino else ""
    c.drawString(18 * mm, _y(34.5), orig)
    c.drawString(64 * mm, _y(34.5), dest)

    # ── REMITE (5, 36, 92, 10) ────────────────────────────────────────────────
    _rect(c, 5, 36, 92, 10)
    _bold(c, 7)
    c.drawString(6 * mm,  _y(39), "REMITE:")
    c.drawString(70 * mm, _y(39), "NIT:")
    c.drawString(6 * mm,  _y(42), "DIR:")
    c.drawString(70 * mm, _y(42), "TEL:")
    c.drawString(6 * mm,  _y(45), "DOCUMENTO:")
    _regular(c, 7)
    c.drawString(18 * mm, _y(39), _safe(guia, "nombre_remitente")[:33])
    c.drawString(76 * mm, _y(39), _safe(guia.tercero, "numero_identificacion"))
    c.drawString(13 * mm, _y(42), _safe(guia, "direccion_remitente")[:38])
    c.drawString(76 * mm, _y(42), _safe(guia, "telefono_remitente"))
    c.drawString(24 * mm, _y(45), _safe(guia, "documento_cliente"))

    # ── DESTINATARIO (5, 46, 92, 10) ──────────────────────────────────────────
    _rect(c, 5, 46, 92, 10)
    _bold(c, 7)
    c.drawString(6 * mm,  _y(50), "DESTINO:")
    c.drawString(70 * mm, _y(50), "DOC:")
    c.drawString(6 * mm,  _y(54), "DIR:")
    c.drawString(70 * mm, _y(54), "TEL:")
    _regular(c, 7)
    c.drawString(18 * mm, _y(50), _safe(guia, "nombre_destinatario")[:32])
    cod_id = _safe(guia, "codigo_identificacion_destinatario_fk")
    num_id = _safe(guia, "numero_identificacion_destinatario")[:12]
    ident = f"{cod_id} {num_id}".strip()
    c.drawString(77 * mm, _y(50), ident)
    c.drawString(13 * mm, _y(54), _safe(guia, "direccion_destinatario")[:41])
    c.drawString(76 * mm, _y(54), _safe(guia, "telefono_destinatario")[:10])

    # ── LIQUIDACIÓN (5, 56, 44, 23) ───────────────────────────────────────────
    vr_flete   = float(guia.vr_flete or 0)
    vr_manejo  = float(guia.vr_manejo or 0)
    vr_total   = vr_flete + vr_manejo
    vr_declara = float(guia.vr_declara or 0)

    _rect(c, 5, 56, 44, 5)
    _bold(c, 7)
    c.drawString(6 * mm, _y(59), "LIQUIDACION")

    _rect(c, 5, 61, 44, 18)
    for lbl, val, y_pos in [
        ("FLETE:",  _num(vr_flete),  64),
        ("MANEJO:", _num(vr_manejo), 67),
        ("OTROS:",  "0",             70),
        ("TOTAL:",  _num(vr_total),  73),
    ]:
        _bold(c, 7)
        c.drawString(7 * mm, _y(y_pos), lbl)
        bold = (lbl == "TOTAL:")
        if bold: _bold(c, 7)
        else:    _regular(c, 7)
        c.drawRightString(48 * mm, _y(y_pos), val)

    _bold(c, 7)
    c.drawString(7 * mm,  _y(77), "Valor declarado")
    c.drawString(30 * mm, _y(77), _num(vr_declara))

    # ── UND / PESO / VOL (49, 56, 48, 5) ──────────────────────────────────────
    _rect(c, 49, 56, 48, 5)
    _bold(c, 7)
    c.drawString(51 * mm, _y(59), "UND:")
    c.drawString(65 * mm, _y(59), "PESO:")
    c.drawString(82 * mm, _y(59), "VOL:")
    _regular(c, 7)
    c.drawString(58 * mm, _y(59), _num(guia.unidades))
    c.drawString(73 * mm, _y(59), _num(guia.peso_real))
    c.drawString(89 * mm, _y(59), _num(guia.peso_volumen))

    # ── FIRMA DESTINATARIO (49, 61, 48, 18) ───────────────────────────────────
    _rect(c, 49, 61, 48, 18)
    _regular(c, 5)
    c.drawString(50 * mm, _y(64), "Fecha Recib:")
    c.setFillColorRGB(0.78, 0.78, 0.78)
    c.drawString(61 * mm, _y(64), "DD MM AAAA")
    c.setFillColorRGB(0, 0, 0)
    c.drawString(76 * mm, _y(64), "Hora:")
    c.setFillColorRGB(0.78, 0.78, 0.78)
    c.drawString(82 * mm, _y(64), "HH: MM")
    c.setFillColorRGB(0, 0, 0)

    _line(c, 52, 75, 92, 75)   # línea de firma
    _bold(c, 7)
    c.drawString(58 * mm, _y(78), "FIRMA DESTINATARIO")

    # ── COMENTARIOS (5, 79, 92, 12) ───────────────────────────────────────────
    _rect(c, 5, 79, 92, 12)
    coment = _safe(guia, "comentario")[:250]
    if coment:
        _bold(c, 7)
        lines = _wrap(coment, 88, "Helvetica-Bold", 7)[:4]
        for k, line in enumerate(lines):
            c.drawString(6 * mm, _y(82 + k * 3), line)

    # ── Footer ────────────────────────────────────────────────────────────────
    _regular(c, 6)
    if not (guia.contenido_verificado or False):
        c.drawString(5 * mm, _y(93), "Sin verificar contenido")
    c.drawString(50 * mm, _y(93), f"Usuario: {_safe(guia, 'usuario')}")

    # Mensaje legal / política de la empresa
    _regular(c, 4.5)
    c.drawString(5 * mm, _y(95.5),
        "Consulta estado de envío, tratamiento de datos, términos y condiciones: "
        f"{_safe(config, 'sitio_web')}")

    _regular(c, 5)
    c.drawString(60 * mm, _y(97.8),
                 f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [Semantica ERP | Logistica]")


# ── Función pública ───────────────────────────────────────────────────────────

def generar_pagina(c, guia, config, logo=None):
    """Dibuja una copia de la guía en una página 100×100 mm."""
    logo_img = _logo_image(logo)
    _draw_copy(c, guia, config, logo_img)

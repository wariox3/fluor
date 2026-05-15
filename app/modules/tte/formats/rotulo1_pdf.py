"""
Rótulo formato 1 — página cuadrada 100×100 mm.
Coordenadas en mm, origen superior-izquierdo (igual que FPDF).
"""
from datetime import datetime

from reportlab.lib.units import mm
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

PAGE_SIZE = (100 * mm, 100 * mm)

_W, _H = PAGE_SIZE


# ── Conversión de coordenadas FPDF → ReportLab ──────────────────────────────────

def _y(y_mm: float) -> float:
    """Baseline Y desde top (FPDF) → baseline Y desde bottom (ReportLab)."""
    return _H - y_mm * mm


def _iy(y_mm: float, h_mm: float) -> float:
    """Esquina inferior-izquierda de imagen/rect en ReportLab."""
    return _H - (y_mm + h_mm) * mm


# ── Helpers de datos ─────────────────────────────────────────────────────────────

def _safe(obj, *attrs, default: str = "") -> str:
    for attr in attrs:
        if obj is None:
            return default
        obj = getattr(obj, attr, None)
    return str(obj) if obj is not None else default


def _ciudad(ciudad_obj) -> str:
    if not ciudad_obj:
        return ""
    return f"{_safe(ciudad_obj, 'nombre')} {_safe(ciudad_obj, 'nombre_division')}".strip()


def _fecha(dt) -> str:
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M") if hasattr(dt, "strftime") else str(dt)


# ── Helpers de dibujo ────────────────────────────────────────────────────────────

def _qr(value: str, size_mm: float) -> Drawing:
    qr = QrCodeWidget(str(value))
    b = qr.getBounds()
    w, h = b[2] - b[0], b[3] - b[1]
    sz = size_mm * mm
    d = Drawing(sz, sz, transform=[sz / w, 0, 0, sz / h, 0, 0])
    d.add(qr)
    return d


def _bold(c, size: int):
    c.setFont("Helvetica-Bold", size)


def _regular(c, size: int):
    c.setFont("Helvetica", size)


# ── Función pública ──────────────────────────────────────────────────────────────

def generar_pagina(c, guia, pieza: int, total: int, config):
    """Dibuja un rótulo en la página actual del canvas."""

    nombre   = _safe(config, "nombre")[:40]
    nit      = f"NIT {_safe(config, 'nit')}-{_safe(config, 'digito_verificacion')}"
    telefono = f"TELEFONO: {_safe(config, 'telefono')}"

    # ── Encabezado empresa (Bold 10, centrado) ───────────────────────────────────
    # Cell(85,5,nombre,C) en SetXY(5,5)  → center_x=47.5mm, baseline≈9.3mm
    # Cell(80,5,nit,C)   en SetXY(5,10) → center_x=45mm,   baseline≈14.3mm
    # Cell(80,5,tel,C)   en SetXY(5,15) → center_x=45mm,   baseline≈19.3mm
    _bold(c, 10)
    c.drawCentredString(47.5 * mm, _y(9.3),  nombre)
    c.drawCentredString(45.0 * mm, _y(14.3), nit)
    c.drawCentredString(45.0 * mm, _y(19.3), telefono)

    # ── QR code — Image(70, 10, 20, 20) ─────────────────────────────────────────
    renderPDF.draw(_qr(str(guia.codigo_guia_pk), 20), c, 70 * mm, _iy(10, 20))

    # ── Número de guía (Bold 12) y tipo de servicio (Bold 9) ─────────────────────
    _bold(c, 12)
    c.drawString(5 * mm, _y(25), f"GUIA No. {guia.codigo_guia_pk}")
    _bold(c, 9)
    c.drawString(5 * mm, _y(30), _safe(guia.guia_tipo, "nombre").upper() if guia.guia_tipo else "")

    # ── Etiquetas remitente (Bold 7) ─────────────────────────────────────────────
    _bold(c, 7)
    for label, x_mm, y_mm in [
        ("FECHA:",        5,  34),
        ("DOC-CLIENTE:", 37,  34),
        ("REMITENTE:",    5,  38),
        ("DIRECCION:",    5,  42),
        ("ORIGEN:",       5,  46),
        ("EMPAQUE:",      5,  50),
        ("PESO:",         5,  54),
        ("VOLUMEN:",     30,  54),
        ("RELACION:",    60,  54),
    ]:
        c.drawString(x_mm * mm, _y(y_mm), label)

    # ── Valores remitente (Regular 7) ────────────────────────────────────────────
    _regular(c, 7)
    for text, x_mm, y_mm in [
        (_fecha(guia.fecha_ingreso),                           15, 34),
        (_safe(guia, "documento_cliente")[:30],                55, 34),
        (_safe(guia, "nombre_remitente"),                      21, 38),
        (_safe(guia, "direccion_remitente"),                   21, 42),
        (_ciudad(guia.ciudad_origen),                          21, 46),
        (_safe(guia.empaque, "nombre") if guia.empaque else "", 21, 50),
        (str(int(guia.peso_real or 0)),                        15, 54),
        (str(int(guia.peso_volumen or 0)),                     45, 54),
        (_safe(guia, "relacion_cliente"),                      74, 54),
    ]:
        c.drawString(x_mm * mm, _y(y_mm), str(text))

    # ── Línea separadora — Line(5,56,96,56) ─────────────────────────────────────
    c.line(5 * mm, _y(56), 96 * mm, _y(56))

    # ── Etiquetas destinatario (Bold 7) ──────────────────────────────────────────
    _bold(c, 7)
    for label, x_mm, y_mm in [
        ("DESTINATARIO:", 5, 60),
        ("DIRECCION:",    5, 64),
        ("DESTINO:",      5, 68),
        ("TELEFONO:",     5, 72),
        ("COMENTARIOS:",  5, 76),
    ]:
        c.drawString(x_mm * mm, _y(y_mm), label)

    # ── Valores destinatario (Regular 7) ─────────────────────────────────────────
    _regular(c, 7)
    for text, x_mm, y_mm in [
        (_safe(guia, "nombre_destinatario"),    25, 60),
        (_safe(guia, "direccion_destinatario"), 20, 64),
        (_ciudad(guia.ciudad_destino),          20, 68),
        (_safe(guia, "telefono_destinatario"),  20, 72),
        (_safe(guia, "comentario"),             25, 76),
    ]:
        c.drawString(x_mm * mm, _y(y_mm), str(text))

    # ── Caja ZONA — Rect(80,65,16,4) + Rect(80,69,16,9) ─────────────────────────
    c.rect(80 * mm, _iy(65, 4), 16 * mm,  4 * mm)
    c.rect(80 * mm, _iy(69, 9), 16 * mm,  9 * mm)
    _bold(c, 7)
    c.drawString(85 * mm, _y(68), "ZONA")
    _bold(c, 16)
    c.drawString(81 * mm, _y(75), _safe(guia, "franja"))

    # ── Línea separadora — Line(5,78,96,78) ─────────────────────────────────────
    c.line(5 * mm, _y(78), 96 * mm, _y(78))

    # ── Footer: operación ingreso y usuario ──────────────────────────────────────
    _bold(c, 7)
    c.drawString(5  * mm, _y(82), "OPERACION INGRESO:")
    c.drawString(5  * mm, _y(85), "USUARIO:")
    _regular(c, 7)
    c.drawString(35 * mm, _y(82), _safe(guia, "codigo_operacion_ingreso_fk"))
    c.drawString(20 * mm, _y(85), _safe(guia, "usuario"))

    # ── Cobro en entrega (condicional) ───────────────────────────────────────────
    vr_cobro = guia.vr_cobro_entrega or 0
    if vr_cobro > 0:
        _bold(c, 7)
        c.drawString(55 * mm, _y(82), "COBRO ENTREGA:")
        _regular(c, 8)
        c.drawString(80 * mm, _y(82), f"{vr_cobro:,.0f}")

    # ── PIEZA X / Y (Bold 14) ────────────────────────────────────────────────────
    _bold(c, 14)
    c.drawString(58 * mm, _y(90), f"PIEZA {pieza} / {total}")

    # ── Timestamp (Regular 5) ────────────────────────────────────────────────────
    _regular(c, 5)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.drawString(58 * mm, _y(93), f"{ts} [Semantica ERP | Logistica]")

    # ── Código de barras — Image(5,86,50,8), valor: {guia}U{pieza} ───────────────
    bc_value = f"{guia.codigo_guia_pk}U{pieza}"
    bc = createBarcodeDrawing("Code128", value=bc_value, barHeight=8 * mm, barWidth=1.1, humanReadable=False)
    renderPDF.draw(bc, c, 5 * mm, _iy(86, 8))

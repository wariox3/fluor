"""
Rótulo formato 2 — etiqueta pequeña 50×20 mm.
Coordenadas en mm, origen superior-izquierdo (igual que FPDF).
Sin encabezado de empresa ni código de barras.
"""
from reportlab.lib.units import mm
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

PAGE_SIZE = (50 * mm, 20 * mm)

_W, _H = PAGE_SIZE


# ── Conversión de coordenadas FPDF → ReportLab ──────────────────────────────────

def _y(y_mm: float) -> float:
    return _H - y_mm * mm


def _iy(y_mm: float, h_mm: float) -> float:
    return _H - (y_mm + h_mm) * mm


# ── Helpers ──────────────────────────────────────────────────────────────────────

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
    """Dibuja un rótulo formato 2 en la página actual del canvas."""

    # ── QR code — Image(39, 5, 10, 10) ──────────────────────────────────────────
    renderPDF.draw(_qr(str(guia.codigo_guia_pk), 10), c, 39 * mm, _iy(5, 10))

    # ── GUIA No. (Bold 5) ────────────────────────────────────────────────────────
    _bold(c, 5)
    c.drawString(2 * mm, _y(3), f"GUIA No. {guia.codigo_guia_pk}")

    # ── DOC CLIENTE (Bold 6 label / Regular 6 valor) ─────────────────────────────
    _bold(c, 6)
    c.drawString(2 * mm, _y(5.5), "DOC CLIENTE:")
    _regular(c, 6)
    c.drawString(18 * mm, _y(5.5), _safe(guia, "documento_cliente")[:16])

    # ── Campos Bold 4 / Regular 4 ────────────────────────────────────────────────
    filas = [
        ("DESTINATARIO:", 2, 14, 8,  _safe(guia, "nombre_destinatario")[:24]),
        ("DIRECCIÓN:",    2, 11, 10, _safe(guia, "direccion_destinatario")[:24]),
        ("DESTINO:",      2,  9, 12, _ciudad(guia.ciudad_destino)[:24]),
        ("REMITENTE:",    2, 11, 14, _safe(guia, "nombre_remitente")[:24]),
    ]
    for label, lx, vx, y_mm, valor in filas:
        _bold(c, 4)
        c.drawString(lx * mm, _y(y_mm), label)
        _regular(c, 4)
        c.drawString(vx * mm, _y(y_mm), valor)

    # ── ZONA label + franja (Bold 4) ─────────────────────────────────────────────
    _bold(c, 4)
    c.drawString(2 * mm, _y(18), "ZONA")
    c.drawString(2 * mm, _y(19), _safe(guia, "franja"))

    # ── PIEZA X / Y (Bold 4) ─────────────────────────────────────────────────────
    c.drawString(11 * mm, _y(18), f"PIEZA {pieza} / {total}")

    # ── Cobro en entrega (condicional, Bold 5) ───────────────────────────────────
    vr_cobro = guia.vr_cobro_entrega or 0
    if vr_cobro > 0:
        _bold(c, 5)
        c.drawString(39 * mm, _y(18), f"${vr_cobro:,.0f}")

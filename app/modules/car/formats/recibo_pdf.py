"""
Formato PDF de los movimientos de cartera que ve el cliente en el portal.

Port de `App\\Formato\\Cartera\\Recibo` (recibos de caja, clase `RC`) y
`App\\Formato\\Cartera\\Anticipo` (anticipos, clase `AN`) de holmio: encabezado de la empresa con el
nombre del tipo de movimiento, datos del movimiento, tabla de las cuentas que afecta con su
contrapartida en la cuenta bancaria, línea "Responsable" y marca de agua "ANULADO" o
"SIN APROBAR". Ambos formatos comparten la tabla y difieren en los datos del encabezado.

Holmio siempre imprime en carta; el tamaño de papel de `gen_formato` 11 no se replica.
"""

from dataclasses import dataclass
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.pdf_header import encabezado_pdf

# Clases de movimiento con formato, como `CarMovimientoRepository::generarFormato` de holmio
CLASE_RECIBO = "RC"
CLASE_ANTICIPO = "AN"
CLASES_CON_FORMATO = (CLASE_RECIBO, CLASE_ANTICIPO)

# ── Página: holmio usa 10 mm de margen y una grilla de 191 mm ─────────────────────
_MARGIN = 10 * mm
_W = letter[0] - 2 * _MARGIN

# ── Colores (los grises de holmio) ─────────────────────────────────────────────
_GRIS_LBL = colors.Color(200 / 255, 200 / 255, 200 / 255)
_GRIS_TH = colors.Color(236 / 255, 236 / 255, 236 / 255)
_MARCA_AGUA = colors.Color(1, 220 / 255, 220 / 255)

_S = {
    "lbl": ParagraphStyle("rc_lbl", fontSize=8, leading=10, fontName="Helvetica-Bold"),
    "val": ParagraphStyle("rc_val", fontSize=8, leading=10),
    "val_r": ParagraphStyle("rc_val_r", fontSize=8, leading=10, alignment=TA_RIGHT),
    "th": ParagraphStyle("rc_th", fontSize=7, leading=9, fontName="Helvetica-Bold", alignment=TA_CENTER),
    "th_l": ParagraphStyle("rc_th_l", fontSize=7, leading=9, fontName="Helvetica-Bold"),
    "td": ParagraphStyle("rc_td", fontSize=7, leading=9),
    "td_r": ParagraphStyle("rc_td_r", fontSize=7, leading=9, alignment=TA_RIGHT),
}

# Columnas de holmio: COD | NUM | NIT | TERCERO | CTA BAN | BANCO | CTA CON | DÉBITO | CRÉDITO
_ANCHOS_DETALLE = [w * mm for w in (11, 15, 15, 50, 20, 20, 20, 20, 20)]
# Datos del encabezado: etiqueta | valor | etiqueta | valor
_ANCHOS_DATOS = [30 * mm, 66 * mm, 40 * mm, 55 * mm]


@dataclass
class DatosMovimiento:
    """Movimiento con lo que imprime holmio (`reciboImprimir` / `anticipoImprimir`)."""

    codigo_movimiento_pk: int
    codigo_movimiento_clase_fk: str
    movimiento_tipo: str | None
    numero: int | None
    fecha: object
    fecha_documento: object
    vr_total_neto: float | None
    estado_aprobado: bool | None
    estado_anulado: bool | None
    comentarios: str | None
    usuario: str | None
    tercero_nombre_corto: str | None
    tercero_numero_identificacion: str | None
    tercero_direccion: str | None
    tercero_telefono: str | None
    cuenta_cuenta: str | None
    cuenta_codigo_cuenta_contable_fk: str | None
    banco_nombre: str | None


@dataclass
class DetalleMovimiento:
    """Cuenta afectada por el movimiento (`CarMovimientoDetalleRepository::listaFormato`)."""

    codigo_cuenta_cobrar_tipo_fk: str | None
    numero: str | None
    tercero_numero_identificacion: str | None
    tercero_nombre_corto: str | None
    codigo_cuenta_fk: str | None
    naturaleza: str | None
    vr_pago: float | None


def _p(texto, estilo: str) -> Paragraph:
    contenido = escape(str(texto)) if texto is not None else ""
    return Paragraph(contenido.replace("\r\n", "\n").replace("\n", "<br/>"), _S[estilo])


def _fecha(valor) -> str:
    return valor.strftime("%Y-%m-%d") if valor else ""


def _dinero(valor) -> str:
    """Como `number_format` de holmio: sin decimales y con coma de miles."""
    return f"{round(valor or 0):,}"


def _recorte(texto: str | None, largo: int) -> str:
    """Holmio recorta el tercero y el banco para que quepan en la celda."""
    return texto[:largo] if isinstance(texto, str) else ""


def _filas_recibo(m: DatosMovimiento, contabilizar_fecha_movimiento: bool) -> list[list]:
    L, V = (lambda t: _p(t, "lbl")), (lambda t: _p(t, "val"))
    # Holmio solo muestra la fecha de elaboración si la empresa contabiliza con ella
    titulo_elaboracion = "FECHA ELABORACION" if contabilizar_fecha_movimiento else ""
    fecha_elaboracion = _fecha(m.fecha) if contabilizar_fecha_movimiento else ""
    return [
        [L("TIPO:"), V(m.movimiento_tipo), L("NÚMERO:"), _p(m.numero, "val_r")],
        [L("TERCERO:"), V(m.tercero_nombre_corto), L("FECHA:"), V(_fecha(m.fecha_documento))],
        [L("IDENTIFICACIÓN:"), V(m.tercero_numero_identificacion), L(titulo_elaboracion), V(fecha_elaboracion)],
        [L("TELÉFONO"), V(m.tercero_telefono), L("TOTAL NETO:"), _p(_dinero(m.vr_total_neto), "val_r")],
        [L("USUARIO:"), V(m.usuario), "", ""],
        [L("COMENTARIOS:"), V(m.comentarios), "", ""],
    ]


def _filas_anticipo(m: DatosMovimiento) -> list[list]:
    L, V = (lambda t: _p(t, "lbl")), (lambda t: _p(t, "val"))
    return [
        [L("TERCERO:"), V(m.tercero_nombre_corto), L("NÚMERO:"), _p(m.numero, "val_r")],
        [L("IDENTIFICACIÓN:"), V(m.tercero_numero_identificacion), L("FECHA:"), V(_fecha(m.fecha))],
        [L("DIRECCIÓN"), V(m.tercero_direccion), L("FECHA PAGO:"), V(_fecha(m.fecha_documento))],
        [L("TELÉFONO"), V(m.tercero_telefono), L("TOTAL NETO:"), _p(_dinero(m.vr_total_neto), "val_r")],
        [L("NUM DOCUMENTO"), V(m.numero), L(""), V("")],
        [L("COMENTARIOS:"), V(m.comentarios), "", ""],
    ]


def _tabla_datos(filas: list[list], filas_a_todo_ancho: list[int]) -> Table:
    tabla = Table(filas, colWidths=_ANCHOS_DATOS)
    estilo = TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("BACKGROUND", (0, 0), (0, -1), _GRIS_LBL),
    ])
    for fila in range(len(filas)):
        if fila in filas_a_todo_ancho:
            estilo.add("SPAN", (1, fila), (3, fila))
        else:
            estilo.add("BACKGROUND", (2, fila), (2, fila), _GRIS_LBL)
    tabla.setStyle(estilo)
    return tabla


def _tabla_detalle(m: DatosMovimiento, detalles: list[DetalleMovimiento]) -> Table:
    T = lambda t, estilo="td": _p(t, estilo)
    datos = [[
        _p("COD", "th_l"), _p("NUM", "th_l"), _p("NIT", "th"), _p("TERCERO", "th"), _p("CTA BAN", "th"),
        _p("BANCO", "th"), _p("CTA CON", "th"), _p("DÉBITO", "th"), _p("CRÉDITO", "th"),
    ]]
    # Holmio muestra en cada fila la cuenta bancaria del movimiento, no la del detalle
    cuenta, banco = m.cuenta_cuenta, _recorte(m.banco_nombre, 10)
    for d in detalles:
        debito, credito = (d.vr_pago, 0) if d.naturaleza == "D" else (0, d.vr_pago)
        datos.append([
            T(d.codigo_cuenta_cobrar_tipo_fk), T(d.numero), T(d.tercero_numero_identificacion),
            T(_recorte(d.tercero_nombre_corto, 30)), T(cuenta), T(banco), T(d.codigo_cuenta_fk),
            T(_dinero(debito), "td_r"), T(_dinero(credito), "td_r"),
        ])
    if detalles:
        # Contrapartida: el total del movimiento entra a la cuenta bancaria
        datos.append([
            "", "", "", "", T(cuenta), T(banco), T(m.cuenta_codigo_cuenta_contable_fk),
            T(_dinero(m.vr_total_neto), "td_r"), T(_dinero(0), "td_r"),
        ])

    tabla = Table(datos, colWidths=_ANCHOS_DETALLE, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), _GRIS_TH),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    return tabla


def _marca_agua(m: DatosMovimiento) -> str | None:
    if m.estado_anulado:
        return "ANULADO"
    if not m.estado_aprobado:
        return "SIN APROBAR"
    return None


def _decorar_pagina(m: DatosMovimiento, firma: bool):
    """Marca de agua detrás del contenido y, en el recibo, la línea "Responsable" del pie."""
    marca = _marca_agua(m)

    def dibujar(canvas, _doc):
        if marca:
            canvas.saveState()
            canvas.setFont("Helvetica", 40)
            canvas.setFillColor(_MARCA_AGUA)
            canvas.translate(90 * mm, letter[1] - 125 * mm)
            canvas.rotate(45)
            canvas.drawString(0, 0, marca)
            canvas.restoreState()
        if firma:
            # Holmio la dibuja a 260 mm del borde superior, 80 mm de ancho
            y = letter[1] - 260 * mm
            canvas.saveState()
            canvas.setLineWidth(0.5)
            canvas.line(_MARGIN, y, _MARGIN + 80 * mm, y)
            canvas.setFont("Helvetica-Bold", 9)
            canvas.drawCentredString(_MARGIN + 40 * mm, y - 5 * mm, "Responsable")
            canvas.restoreState()

    return dibujar


def generar(
    movimiento: DatosMovimiento,
    detalles: list[DetalleMovimiento],
    db,
    contabilizar_fecha_movimiento: bool = False,
) -> bytes:
    """PDF del recibo o del anticipo; la clase debe estar en `CLASES_CON_FORMATO`."""
    es_anticipo = movimiento.codigo_movimiento_clase_fk == CLASE_ANTICIPO
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=_MARGIN,
        rightMargin=_MARGIN,
        topMargin=_MARGIN,
        # Espacio para la línea "Responsable" del pie
        bottomMargin=30 * mm,
        title=f"Recibo {movimiento.numero or movimiento.codigo_movimiento_pk}",
    )

    story = encabezado_pdf(titulo=movimiento.movimiento_tipo or "RECIBO", db=db, ancho_util=_W)
    if es_anticipo:
        story.append(_tabla_datos(_filas_anticipo(movimiento), filas_a_todo_ancho=[5]))
    else:
        filas = _filas_recibo(movimiento, contabilizar_fecha_movimiento)
        story.append(_tabla_datos(filas, filas_a_todo_ancho=[4, 5]))
    story.append(Spacer(1, 2 * mm))
    story.append(_tabla_detalle(movimiento, detalles))

    # El anticipo de holmio no tiene la línea "Responsable"
    decorar = _decorar_pagina(movimiento, firma=not es_anticipo)
    doc.build(story, onFirstPage=decorar, onLaterPages=decorar)
    return buffer.getvalue()

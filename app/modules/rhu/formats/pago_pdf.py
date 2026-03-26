from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from app.core.pdf_header import encabezado_pdf

# ── Página ─────────────────────────────────────────────────────────────────────
_MARGIN = 1.5 * cm
_W = letter[0] - 2 * _MARGIN

# ── Colores ────────────────────────────────────────────────────────────────────
_AZUL    = colors.HexColor("#1a3c5e")
_GRIS_BG = colors.HexColor("#dce6f0")
_BORDE   = colors.HexColor("#999999")

# ── Estilos ────────────────────────────────────────────────────────────────────
_S = {
    "lbl":      ParagraphStyle("lbl",     fontSize=7,  fontName="Helvetica-Bold"),
    "val":      ParagraphStyle("val",     fontSize=7),
    "th":       ParagraphStyle("th",      fontSize=7,  fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_CENTER),
    "td":       ParagraphStyle("td",      fontSize=7),
    "td_r":     ParagraphStyle("td_r",    fontSize=7,  alignment=TA_RIGHT),
    "td_c":     ParagraphStyle("td_c",    fontSize=7,  alignment=TA_CENTER),
    "tot_lbl":  ParagraphStyle("tl",      fontSize=8,  fontName="Helvetica-Bold", alignment=TA_RIGHT),
    "tot_val":  ParagraphStyle("tv",      fontSize=8,  alignment=TA_RIGHT),
    "neto_lbl": ParagraphStyle("nl",      fontSize=9,  fontName="Helvetica-Bold", alignment=TA_RIGHT),
    "neto_val": ParagraphStyle("nv",      fontSize=9,  fontName="Helvetica-Bold", alignment=TA_RIGHT),
}

def _p(text, style="val") -> Paragraph:
    return Paragraph(str(text), _S[style])

def _fmt(v) -> str:
    return f"{v:,.0f}" if v is not None else "0"

def _fmt_horas(v) -> str:
    return f"{v:,.2f}" if v is not None else "0.00"

def _fecha(d) -> str:
    return d.strftime("%Y-%m-%d") if d else ""


def _estilo_info_grid() -> TableStyle:
    return TableStyle([
        # Fondo gris en columnas de etiqueta (0, 2, 4)
        ("BACKGROUND",    (0, 0), (0, -1), _GRIS_BG),
        ("BACKGROUND",    (2, 0), (2, -1), _GRIS_BG),
        ("BACKGROUND",    (4, 0), (4, -1), _GRIS_BG),
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",      (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTNAME",      (4, 0), (4, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 7),
        ("GRID",          (0, 0), (-1, -1), 0.3, _BORDE),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
    ])


def _get(obj, *attrs, default="N/A"):
    """Navega una cadena de atributos con fallback seguro."""
    for attr in attrs:
        if obj is None:
            return default
        obj = getattr(obj, attr, None)
    return obj if obj is not None else default


def _seccion_programacion(pago, programacion: list) -> list:
    """Devuelve flowables con el grid de días de la programación."""
    if not programacion:
        return []

    fecha_desde = pago.fecha_desde
    fecha_hasta = pago.fecha_hasta
    if not fecha_desde or not fecha_hasta:
        return []

    dia_ini = fecha_desde.day
    dia_fin = fecha_hasta.day
    if dia_fin == 30:
        dia_fin = 31
    dias = list(range(dia_ini, dia_fin + 1))
    n = len(dias)
    if n == 0:
        return []

    cell_w = _W / n
    col_widths = [cell_w] * n

    # Encabezado de días
    header = [_p(f"D{d}", "th") for d in dias]

    rows = [header]
    for prog in programacion:
        fila = [_p(getattr(prog, f"dia_{d}", "") or "", "td_c") for d in dias]
        rows.append(fila)

    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), _AZUL),
        ("FONTSIZE",      (0, 0), (-1, -1), 6.5),
        ("GRID",          (0, 0), (-1, -1), 0.3, _BORDE),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 1),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 1),
    ]))
    return [Spacer(1, 0.3 * cm), tbl]


def generar(pago, detalles, db=None, programacion=None) -> bytes:
    empleado = pago.empleado
    contrato = pago.contrato_rel

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=_MARGIN, rightMargin=_MARGIN,
        topMargin=_MARGIN,  bottomMargin=_MARGIN,
    )
    story = []
    story += encabezado_pdf(
        titulo="COMPROBANTE DE PAGO DE NÓMINA",
        db=db,
        ancho_util=_W,
    )

    # ── Datos del grid ──────────────────────────────────────────────────────────
    nombre  = _get(empleado, "nombre_corto")
    nro_id  = _get(empleado, "numero_identificacion")
    numero  = str(pago.numero or pago.codigo_pago_pk)
    periodo = _get(pago.periodo_rel, "nombre")
    cuenta  = _get(empleado, "cuenta")
    banco   = _get(empleado, "banco_rel", "nombre")
    cargo   = _get(pago.cargo_rel, "nombre")
    pension = _get(pago.entidad_pension_rel, "nombre_corto")
    salud   = _get(pago.entidad_salud_rel, "nombre_corto")
    grupo   = _get(contrato, "grupo_rel", "nombre")
    puesto_obj = getattr(contrato, "puesto_rel", None) if contrato else None
    puesto  = f"{contrato.codigo_puesto_fk} | {puesto_obj.nombre}" if puesto_obj and contrato else _get(puesto_obj, "nombre")
    cliente = _get(contrato, "tercero_rel", "nombre_corto")
    zona    = _get(empleado, "zona_rel", "nombre")
    salario = _fmt(pago.vr_salario_contrato)

    # Anchos: etiqueta | valor | etiqueta | valor | etiqueta | valor
    cw = [2.2*cm, 4.0*cm, 2.6*cm, 3.0*cm, 2.5*cm, 4.29*cm]

    L = lambda t: _p(t, "lbl")
    V = lambda t: _p(t, "val")

    grid_data = [
        [L("NÚMERO:"),      V(numero),  L("PERIODO:"),        V(periodo),                    L("CUENTA:"),   V(cuenta)  ],
        [L("EMPLEADO:"),    V(nombre),  L("IDENTIFICACIÓN:"), V(nro_id),                     L("BANCO:"),    V(banco)   ],
        [L("CARGO:"),       V(cargo),   L("DESDE:"),          V(_fecha(pago.fecha_desde)),   L("PENSIÓN:"),  V(pension) ],
        [L("GRUPO"),        V(grupo),   L("HASTA:"),          V(_fecha(pago.fecha_hasta)),   L("SALUD:"),    V(salud)   ],
        [L("PUESTO:"),      V(puesto),  L("CLIENTE:"),        V(cliente),                    L("ZONA:"),     V(zona)    ],
        [V(""),             V(""),      V(""),                V(""),                         L("SALARIO:"),  _p(salario, "td_r")],
        [L("COMENTARIO:"),  V(""),      V(""),                V(""),                         V(""),          V("")       ],
    ]

    grid = Table(grid_data, colWidths=cw)
    grid_style = _estilo_info_grid()
    grid_style.add("SPAN", (1, 6), (5, 6))   # valor comentario ocupa cols 1-5
    grid_style.add("SPAN", (0, 5), (3, 5))   # celda vacía antes de SALARIO
    grid_style.add("BACKGROUND", (0, 5), (3, 5), colors.white)
    grid_style.add("FONTNAME", (0, 5), (3, 5), "Helvetica")
    grid_style.add("BACKGROUND", (1, 6), (5, 6), colors.white)  # limpiar grises dentro del span
    grid.setStyle(grid_style)
    story.append(grid)
    story.append(Spacer(1, 0.3 * cm))

    # ── Tabla de conceptos ─────────────────────────────────────────────────────
    ccw = [0.8*cm, 5.3*cm, 3.0*cm, 1.5*cm, 1.2*cm, 1.0*cm, 2.8*cm, 2.99*cm]

    conceptos_header = [
        _p("COD", "th"), _p("CONCEPTO", "th"), _p("DETALLE", "th"),
        _p("HORAS", "th"), _p("DÍAS", "th"), _p("%", "th"),
        _p("DEVENGADO", "th"), _p("DEDUCCIÓN", "th"),
    ]

    def fila_detalle(d):
        return [
            _p(d.codigo_concepto_fk or "", "td_c"),
            _p(d.concepto_nombre or "", "td"),
            _p(d.detalle or "", "td"),
            _p(_fmt_horas(d.horas) if d.horas else "", "td_c"),
            _p(_fmt(d.dias) if d.dias else "", "td_c"),
            _p(_fmt(d.porcentaje) if d.porcentaje else "", "td_c"),
            _p(_fmt(d.vr_devengado), "td_r"),
            _p(_fmt(d.vr_deduccion), "td_r"),
        ]

    conceptos_data = [conceptos_header] + [fila_detalle(d) for d in (detalles or [])]

    conceptos_table = Table(conceptos_data, colWidths=ccw, repeatRows=1)
    conceptos_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), _AZUL),
        ("FONTSIZE",      (0, 0), (-1, -1), 7),
        ("GRID",          (0, 0), (-1, -1), 0.3, _BORDE),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
    ]))
    story.append(conceptos_table)
    story.append(Spacer(1, 0.3 * cm))

    # ── Totales (derecha) ──────────────────────────────────────────────────────
    tot_cw = [_W - 5.6 * cm, 2.9 * cm, 2.7 * cm]

    totales_data = [
        [_p(""), _p("DEVENGADO:",   "tot_lbl"), _p(_fmt(pago.vr_devengado),              "tot_val")],
        [_p(""), _p("DEDUCCIONES:", "tot_lbl"), _p(f"-{_fmt(pago.vr_deduccion)}",        "tot_val")],
        [_p(""), _p("NETO PAGAR",   "neto_lbl"), _p(_fmt(pago.vr_neto),                  "neto_val")],
    ]

    totales_table = Table(totales_data, colWidths=tot_cw)
    totales_table.setStyle(TableStyle([
        ("GRID",          (1, 0), (2, -1), 0.3, _BORDE),
        ("BACKGROUND",    (1, 2), (2, 2),  _GRIS_BG),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
    ]))
    story.append(totales_table)

    story += _seccion_programacion(pago, programacion or [])

    doc.build(story)
    return buffer.getvalue()

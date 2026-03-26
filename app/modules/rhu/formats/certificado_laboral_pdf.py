from io import BytesIO
from datetime import date, datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, Image
from app.core.pdf_header import _blob_to_bytes

_MARGIN_H = 3.0 * cm
_MARGIN_V = 2.5 * cm
_W = letter[0] - 2 * _MARGIN_H

_GRIS = colors.HexColor("#555555")

_S = {
    "ts":       ParagraphStyle("ts",      fontSize=7,  textColor=_GRIS, alignment=TA_RIGHT),
    "dept":     ParagraphStyle("dept",    fontSize=11, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4),
    "titulo":   ParagraphStyle("titulo",  fontSize=11, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4),
    "asunto":   ParagraphStyle("asunto",  fontSize=11, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=20),
    "cuerpo":   ParagraphStyle("cuerpo",  fontSize=10, leading=16, alignment=TA_JUSTIFY, spaceAfter=12),
    "firma_n":  ParagraphStyle("firma_n", fontSize=10, fontName="Helvetica-Bold"),
    "firma_c":  ParagraphStyle("firma_c", fontSize=10),
    "footer":   ParagraphStyle("footer",  fontSize=8,  textColor=_GRIS, alignment=TA_RIGHT),
}

_MESES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]


def _fecha_larga(d: date) -> str:
    return f"{d.day} de {_MESES[d.month]} de {d.year}"


def _fmt(v) -> str:
    if v is None:
        return "0"
    return f"{v:,.0f}".replace(",", ".")


def generar(empleado, contrato, config=None, gen_imagen=None) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=_MARGIN_H,
        rightMargin=_MARGIN_H,
        topMargin=_MARGIN_V,
        bottomMargin=_MARGIN_V,
    )

    # ── Datos empresa desde config ──────────────────────────────────────────────
    empresa_nombre    = getattr(config, "nombre",             "EMPRESA DEMO S.A.S").upper() if config else "EMPRESA DEMO S.A.S"
    nit_raw           = getattr(config, "nit",                "900000000")                  if config else "900000000"
    dv                = getattr(config, "digito_verificacion", "0")                         if config else "0"
    empresa_nit       = f"{nit_raw}-{dv}"
    empresa_tel       = getattr(config, "telefono",           "")                           if config else ""
    empresa_email     = getattr(config, "correo",             "")                           if config else ""
    empresa_dir       = getattr(config, "direccion",          "")                           if config else ""
    empresa_ciudad    = getattr(config, "ciudad",             "la ciudad")                  if config else "la ciudad"

    # ── Datos empleado / contrato ───────────────────────────────────────────────
    nombre            = getattr(empleado, "nombre_corto", "N/A").upper()
    identificacion    = getattr(empleado, "numero_identificacion", "N/A")
    fecha_inicio      = contrato.fecha_desde.strftime("%Y-%m-%d") if contrato.fecha_desde else "N/A"
    tipo_contrato     = getattr(contrato, "tipo_contrato", "CONTRATO TÉRMINO INDEFINIDO").upper()
    cargo             = getattr(contrato, "cargo", "N/A").upper()
    salario           = _fmt(getattr(contrato, "vr_salario", 0))
    auxilio_transp    = _fmt(getattr(contrato, "vr_auxilio_transporte", 0))
    vr_adicional      = _fmt(getattr(contrato, "vr_adicional", 0))
    vr_promedio       = _fmt(getattr(contrato, "vr_promedio_mensual", 0))
    responsable       = getattr(contrato, "responsable_nombre", empresa_nombre).upper()
    responsable_cargo = getattr(contrato, "responsable_cargo", "DIRECTOR(A) TALENTO HUMANO").upper()

    hoy      = date.today()
    fecha_hoy = _fecha_larga(hoy)

    story = []

    # ── Timestamp ──────────────────────────────────────────────────────────────
    story.append(Paragraph(
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [Semantica | ERP]",
        _S["ts"]
    ))
    story.append(Spacer(1, 0.4 * cm))

    # ── Logo (alineado a la izquierda, sin tabla de empresa) ───────────────────
    if gen_imagen:
        data = _blob_to_bytes(gen_imagen.imagen)
        if data:
            try:
                img = Image(BytesIO(data), width=3.0 * cm, height=3.0 * cm)
                img.hAlign = "LEFT"
                story.append(img)
            except Exception:
                pass
    story.append(Spacer(1, 0.6 * cm))

    # ── Títulos ─────────────────────────────────────────────────────────────────
    story.append(Paragraph("DEPARTAMENTO DE TALENTO HUMANO", _S["dept"]))
    story.append(Paragraph("CERTIFICACIÓN LABORAL", _S["titulo"]))
    story.append(Paragraph("A QUIEN PUEDA INTERESAR", _S["asunto"]))

    # ── Párrafo 1: datos laborales ─────────────────────────────────────────────
    story.append(Paragraph(
        f"Que el(la) señor(a) <b>{nombre}</b>, identificado(a) con C.C. <b>{identificacion}</b> "
        f"labora en <b>{empresa_nombre}</b> Nit. <b>{empresa_nit}</b> desde el <b>{fecha_inicio}</b>, "
        f"mediante un contrato de trabajo <b>{tipo_contrato}</b>.",
        _S["cuerpo"]
    ))

    # ── Párrafo 2: cargo y salario ─────────────────────────────────────────────
    story.append(Paragraph(
        f"Se desempeña en el cargo de <b>{cargo}</b>, de tiempo completo, un salario básico mensual "
        f"de <b>{salario}</b>, más auxilio de transporte <b>{auxilio_transp}</b>, más un valor "
        f"adicional no prestacional por: <b>{vr_adicional}</b>, más recargos de ley con un promedio "
        f"mensual de <b>{vr_promedio}</b>.",
        _S["cuerpo"]
    ))

    # ── Párrafo 3: protección datos ────────────────────────────────────────────
    story.append(Paragraph(
        f"De acuerdo con la <b>LEY 1581 DE 2012 POR LA CUAL SE DICTAN DISPOSICIONES GENERALES "
        f"PARA LA PROTECCIÓN DE DATOS PERSONALES</b>, {empresa_nombre} requiere del consentimiento "
        f"libre previo expreso e informado del titular de los datos personales para el tratamiento "
        f"de estos, excepto en los casos expresamente autorizados en la ley.",
        _S["cuerpo"]
    ))

    # ── Párrafo 4: confirmación datos ──────────────────────────────────────────
    story.append(Paragraph(
        f"Según lo anterior, en caso de requerir confirmación de estos datos, por la entidad donde "
        f"se entrega el certificado, el empleado deberá presentarse a la Oficina de Personal para "
        f"firmar el formato \"autorización para suministrar datos personales\" y de esta forma "
        f"autorizar a {empresa_nombre}, para el tratamiento de estos.",
        _S["cuerpo"]
    ))

    # ── Párrafo 5: cierre ──────────────────────────────────────────────────────
    story.append(Paragraph(
        f"Para constancia se firma en la ciudad de {empresa_ciudad}, el día <b>{fecha_hoy}</b> "
        f"a solicitud del interesado.",
        _S["cuerpo"]
    ))

    # ── Párrafo 6: validación ──────────────────────────────────────────────────
    if empresa_tel or empresa_email:
        story.append(Paragraph(
            f"Si requiere validación del presente documento, comunicarse al celular "
            f"<b>{empresa_tel}</b> - e-mail <b>{empresa_email}</b>.",
            _S["cuerpo"]
        ))

    story.append(Spacer(1, 1.8 * cm))

    # ── Firma ──────────────────────────────────────────────────────────────────
    firma_data = [[Paragraph("_" * 30, _S["firma_c"]), Paragraph("", _S["firma_c"])]]
    firma_table = Table(firma_data, colWidths=[8 * cm, _W - 8 * cm])
    firma_table.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))
    story.append(firma_table)

    firma_info = [
        [Paragraph(responsable,       _S["firma_n"]), Paragraph("", _S["firma_c"])],
        [Paragraph(responsable_cargo, _S["firma_c"]), Paragraph("", _S["firma_c"])],
        [Paragraph(f"NIT {empresa_nit}", _S["firma_c"]), Paragraph("", _S["firma_c"])],
    ]
    info_table = Table(firma_info, colWidths=[8 * cm, _W - 8 * cm])
    info_table.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(info_table)

    story.append(Spacer(1, 1.0 * cm))

    # ── Footer ─────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width=_W, thickness=0.5, color=_GRIS))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"{empresa_tel} &nbsp;&nbsp;|&nbsp;&nbsp; {empresa_email} &nbsp;&nbsp;|&nbsp;&nbsp; {empresa_dir}",
        _S["footer"]
    ))

    doc.build(story)
    return buffer.getvalue()

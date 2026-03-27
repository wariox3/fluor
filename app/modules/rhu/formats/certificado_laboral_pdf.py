from io import BytesIO
from datetime import date, datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from app.core.pdf_header import _blob_to_bytes

_MARGIN_H = 3.0 * cm
_MARGIN_V = 2.5 * cm

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


def _reemplazar_etiquetas(texto: str, datos: dict) -> str:
    for etiqueta, valor in datos.items():
        texto = texto.replace(f"{{{{{etiqueta}}}}}", str(valor) if valor else "")
    return texto


def generar(empleado, contrato, config=None, gen_imagen=None, formato=None) -> bytes:
    fuente_size = 10
    if formato and formato.tamanio_fuente:
        try:
            fuente_size = int(formato.tamanio_fuente)
        except ValueError:
            pass

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=_MARGIN_H,
        rightMargin=_MARGIN_H,
        topMargin=_MARGIN_V,
        bottomMargin=_MARGIN_V,
    )

    # ── Datos para etiquetas ───────────────────────────────────────────────────
    empresa_nombre = getattr(config, "nombre",              "").upper() if config else ""
    nit_raw        = getattr(config, "nit",                 "")         if config else ""
    dv             = getattr(config, "digito_verificacion", "")         if config else ""
    empresa_nit    = f"{nit_raw}-{dv}"
    empresa_tel    = getattr(config, "telefono",  "") if config else ""
    empresa_email  = getattr(config, "correo",    "") if config else ""
    empresa_dir    = getattr(config, "direccion", "") if config else ""
    ciudad_rel     = getattr(config, "ciudad_rel", None) if config else None
    empresa_ciudad = ciudad_rel.nombre if ciudad_rel else ""

    nombre         = getattr(empleado, "nombre_corto",          "").upper()
    identificacion = getattr(empleado, "numero_identificacion",  "")
    fecha_inicio   = contrato.fecha_desde.strftime("%Y-%m-%d") if contrato.fecha_desde else ""
    cargo_rel      = getattr(contrato, "cargo_rel",         None)
    cargo          = cargo_rel.nombre.upper() if cargo_rel else ""
    tipo_rel       = getattr(contrato, "contrato_tipo_rel",  None)
    tipo_contrato  = tipo_rel.nombre.upper() if tipo_rel else ""
    salario        = _fmt(getattr(contrato, "vr_salario", 0))

    etiquetas = {
        "NOMBRE":         nombre,
        "IDENTIFICACION": identificacion,
        "EMPRESA":        empresa_nombre,
        "NIT":            empresa_nit,
        "FECHA_INGRESO":  fecha_inicio,
        "TIPO_CONTRATO":  tipo_contrato,
        "CARGO":          cargo,
        "SALARIO":        salario,
        "CIUDAD":         empresa_ciudad,
        "FECHA_HOY":      _fecha_larga(date.today()),
        "TELEFONO":       empresa_tel,
        "EMAIL":          empresa_email,
        "DIRECCION":      empresa_dir,
    }

    story = []

    # ── Timestamp ──────────────────────────────────────────────────────────────
    story.append(Paragraph(
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [Semantica | ERP]",
        ParagraphStyle("ts", fontSize=7, textColor=colors.HexColor("#555555"), alignment=TA_RIGHT),
    ))
    story.append(Spacer(1, 0.4 * cm))

    # ── Logo ───────────────────────────────────────────────────────────────────
    if gen_imagen:
        data = _blob_to_bytes(gen_imagen.imagen)
        if data:
            try:
                img = Image(BytesIO(data), width=3.0 * cm, height=3.0 * cm)
                img.hAlign = "LEFT"
                story.append(img)
            except Exception:
                pass
    story.append(Spacer(1, 0.4 * cm))

    # ── Contenido desde contenido_externo ──────────────────────────────────────
    contenido = getattr(formato, "contenido_externo", None) if formato else None
    if contenido:
        texto = _reemplazar_etiquetas(contenido, etiquetas)
        story.append(Paragraph(
            texto,
            ParagraphStyle(
                "cuerpo",
                fontSize=fuente_size,
                leading=fuente_size * 1.6,
                alignment=TA_JUSTIFY,
            ),
        ))

    doc.build(story)
    return buffer.getvalue()

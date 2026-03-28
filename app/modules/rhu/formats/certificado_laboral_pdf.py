from datetime import date
from weasyprint import HTML

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


def generar(empleado, contrato, config=None, formato=None) -> bytes:
    fuente_size = 11
    if formato and formato.tamanio_fuente:
        try:
            fuente_size = int(formato.tamanio_fuente)
        except ValueError:
            pass

    # ── Datos para etiquetas ──────────────────────────────────────────────────
    empresa_nombre = getattr(config, "nombre",              "").upper() if config else ""
    nit_raw        = getattr(config, "nit",                 "")         if config else ""
    dv             = getattr(config, "digito_verificacion", "")         if config else ""
    empresa_nit    = f"{nit_raw}-{dv}"
    empresa_tel    = getattr(config, "telefono",  "") if config else ""
    empresa_email  = getattr(config, "correo",    "") if config else ""
    empresa_dir    = getattr(config, "direccion", "") if config else ""
    ciudad_rel     = getattr(config, "ciudad_rel", None) if config else None
    empresa_ciudad = ciudad_rel.nombre if ciudad_rel else ""

    nombre         = getattr(empleado, "nombre_corto",         "").upper()
    identificacion = getattr(empleado, "numero_identificacion", "")
    fecha_inicio   = _fecha_larga(contrato.fecha_desde) if contrato.fecha_desde else ""
    cargo_rel      = getattr(contrato, "cargo_rel",        None)
    cargo          = cargo_rel.nombre.upper() if cargo_rel else ""
    tipo_rel       = getattr(contrato, "contrato_tipo_rel", None)
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

    # ── Contenido con etiquetas reemplazadas ──────────────────────────────────
    contenido = getattr(formato, "contenido_externo", "") or ""
    contenido = _reemplazar_etiquetas(contenido, etiquetas)

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    @page {{
      size: letter;
      margin: 2.5cm 3cm;
    }}
    body {{
      font-family: Arial, sans-serif;
      font-size: {fuente_size}pt;
      color: #000;
    }}
    .contenido p {{
      line-height: 1.6;
      margin: 0 0 0.4cm 0;
    }}
    .ql-align-center {{ text-align: center; }}
    .ql-align-right {{ text-align: right; }}
    .ql-align-justify {{ text-align: justify; }}
  </style>
</head>
<body>
  <div class="contenido">{contenido}</div>
</body>
</html>"""

    return HTML(string=html).write_pdf()

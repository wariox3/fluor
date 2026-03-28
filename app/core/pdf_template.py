from weasyprint import HTML


def _reemplazar_etiquetas(texto: str, datos: dict) -> str:
    for etiqueta, valor in datos.items():
        texto = texto.replace(f"{{{{{etiqueta}}}}}", str(valor) if valor else "")
    return texto


def generar_pdf(etiquetas: dict, formato=None) -> bytes:
    fuente_size = 11
    if formato and formato.tamanio_fuente:
        try:
            fuente_size = int(formato.tamanio_fuente)
        except ValueError:
            pass

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

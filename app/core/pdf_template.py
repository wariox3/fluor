import base64
from weasyprint import HTML


def _reemplazar_etiquetas(texto: str, datos: dict) -> str:
    for etiqueta, valor in datos.items():
        texto = texto.replace(f"{{{{{etiqueta}}}}}", str(valor) if valor else "")
    return texto


def _generar_html_imagenes(imagenes) -> str:
    """Genera divs con position absolute para cada imagen del formato."""
    html_imagenes = ""
    for img in imagenes:
        if not img.imagen:
            continue
        ext = img.extension or "png"
        img_base64 = base64.b64encode(img.imagen).decode("utf-8")
        data_uri = f"data:image/{ext};base64,{img_base64}"

        # Compensar márgenes de @page (2.5cm=25mm arriba, 3cm=30mm izquierda)
        # para posicionar desde el borde real de la página como FPDF
        left = img.posicion_x - 30
        top = img.posicion_y - 25
        style_parts = [
            "position: fixed",
            f"left: {left}mm",
            f"top: {top}mm",
            "z-index: -1",
        ]
        if img.ancho:
            style_parts.append(f"width: {img.ancho}mm")
        if img.alto:
            style_parts.append(f"height: {img.alto}mm")

        style = "; ".join(style_parts)
        html_imagenes += f'<img src="{data_uri}" style="{style};" />\n'
    return html_imagenes


def generar_pdf(etiquetas: dict, formato=None, imagenes=None) -> bytes:
    fuente_size = 11
    if formato and formato.tamanio_fuente:
        try:
            fuente_size = int(formato.tamanio_fuente)
        except ValueError:
            pass

    contenido = getattr(formato, "contenido_externo", "") or ""
    contenido = _reemplazar_etiquetas(contenido, etiquetas)
    contenido = contenido.replace("&nbsp;", " ")

    html_imagenes = ""
    if imagenes:
        html_imagenes = _generar_html_imagenes(imagenes)

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    @page {{
      size: letter;
      margin: 2.5cm 2.5cm;
    }}
    body {{
      font-family: Arial, sans-serif;
      font-size: {fuente_size}pt;
      color: #000;
    }}
    .contenido p {{
      line-height: 1.0;
      margin: 0 0 0.1cm 0;
      text-align: justify;
      min-height: 1em;
    }}
    .contenido p.ql-align-center {{ text-align: center; }}
    .contenido p.ql-align-right {{ text-align: right; }}
    .contenido p.ql-align-justify {{ text-align: justify; }}
  </style>
</head>
<body>
  {html_imagenes}
  <div class="contenido">{contenido}</div>
</body>
</html>"""

    return HTML(string=html).write_pdf()

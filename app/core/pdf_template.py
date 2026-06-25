import atexit
import base64
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from threading import Lock

from app.core.config import PDF_WORKER_MAX_TASKS, PDF_RENDER_TIMEOUT

# ── Pool de subproceso para WeasyPrint ────────────────────────────────────────
# WeasyPrint se apoya en librerías C (Pango/cairo/fontconfig) que filtran memoria
# que el GC de Python no puede recuperar. Para que esa fuga no haga crecer el RSS
# del worker de forma indefinida, el render corre en un subproceso aparte que se
# recicla cada PDF_WORKER_MAX_TASKS renders: al morir, el SO recupera todo.
#
# - mp_context="spawn": el hijo arranca limpio (no se hereda el estado del worker
#   multihilo de uvicorn/gunicorn, evitando deadlocks de fork-en-proceso-con-hilos).
# - max_workers=1: serializa los renders, lo que también acota el pico de memoria.
# - weasyprint se importa SOLO dentro del hijo (ver _render_pdf_bytes), así el
#   proceso padre nunca carga las librerías nativas que filtran.
_executor: ProcessPoolExecutor | None = None
_executor_lock = Lock()


def _get_executor() -> ProcessPoolExecutor:
    global _executor
    if _executor is None:
        with _executor_lock:
            if _executor is None:
                _executor = ProcessPoolExecutor(
                    max_workers=1,
                    max_tasks_per_child=PDF_WORKER_MAX_TASKS,
                    mp_context=mp.get_context("spawn"),
                )
    return _executor


def shutdown_pdf_executor() -> None:
    """Cierra el pool de render. Idempotente; seguro de llamar al apagar la app."""
    global _executor
    with _executor_lock:
        if _executor is not None:
            _executor.shutdown(wait=False, cancel_futures=True)
            _executor = None


atexit.register(shutdown_pdf_executor)


def _render_pdf_bytes(html: str) -> bytes:
    """Renderiza HTML a PDF. Se ejecuta en el subproceso desechable.

    Debe ser una función de nivel de módulo (picklable) para 'spawn'. Importa
    weasyprint aquí dentro para que el proceso padre nunca cargue Pango/cairo.
    """
    from weasyprint import HTML

    return HTML(string=html).write_pdf()


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

    # Render en el subproceso desechable. Si el pool quedó roto (p.ej. el hijo
    # murió por un fallo nativo), se reconstruye y se reintenta una vez.
    try:
        return _get_executor().submit(_render_pdf_bytes, html).result(timeout=PDF_RENDER_TIMEOUT)
    except BrokenProcessPool:
        shutdown_pdf_executor()
        return _get_executor().submit(_render_pdf_bytes, html).result(timeout=PDF_RENDER_TIMEOUT)

from io import BytesIO

from reportlab.pdfgen import canvas as pdf_canvas

from app.modules.tte.formats import guia1_pdf
from app.modules.tte.formats import guia2_pdf
from app.modules.tte.formats import guia3_pdf

# Para agregar un nuevo formato:
#   1. Crear guia{N}_pdf.py con PAGE_SIZE y generar_pagina(c, guia, config)
#   2. Importarlo arriba y registrarlo aquí.
_FORMATOS = {
    1: guia1_pdf,
    2: guia2_pdf,
    3: guia3_pdf,
}


def generar(guias: list, formato: int, db=None) -> bytes:
    modulo = _FORMATOS.get(formato)
    if modulo is None:
        disponibles = ", ".join(str(k) for k in _FORMATOS)
        raise ValueError(f"Formato {formato} no existe. Disponibles: {disponibles}")

    from app.modules.gen.models.configuracion import Configuracion
    from app.modules.gen.models.imagen import Imagen

    config = db.query(Configuracion).first() if db else None
    logo = db.query(Imagen).filter(Imagen.codigo_imagen_pk == "LOGO").first() if db else None

    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=modulo.PAGE_SIZE)

    primera = True
    for guia in guias:
        if not primera:
            c.showPage()
        primera = False
        modulo.generar_pagina(c, guia, config, logo)

    c.save()
    return buffer.getvalue()

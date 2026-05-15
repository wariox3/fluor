from io import BytesIO

from reportlab.pdfgen import canvas as pdf_canvas

from app.modules.tte.formats import rotulo1_pdf
from app.modules.tte.formats import rotulo2_pdf

# Para agregar un nuevo formato:
#   1. Crear rotulo{N}_pdf.py con PAGE_SIZE y generar_pagina(c, guia, pieza, total, config)
#   2. Importarlo arriba y registrarlo aquí.
_FORMATOS = {
    1: rotulo1_pdf,
    2: rotulo2_pdf,
}


def generar(guias: list, formato: int, db=None) -> bytes:
    modulo = _FORMATOS.get(formato)
    if modulo is None:
        disponibles = ", ".join(str(k) for k in _FORMATOS)
        raise ValueError(f"Formato {formato} no existe. Disponibles: {disponibles}")

    from app.modules.gen.models.configuracion import Configuracion
    config = db.query(Configuracion).first() if db else None

    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=modulo.PAGE_SIZE)

    primera = True
    for guia in guias:
        total = max(int(guia.unidades or 1), 1)
        for pieza in range(1, total + 1):
            if not primera:
                c.showPage()
            primera = False
            modulo.generar_pagina(c, guia, pieza, total, config)

    c.save()
    return buffer.getvalue()

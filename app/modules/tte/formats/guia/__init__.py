"""
Formatos de impresión de guías.

Para agregar un formato: crear `guiaN.py` con la clase `GuiaN(FormatoPdf)` decorada con
`@registro.registrar` e importarlo al final de este archivo. La ruta y el motor no cambian.
"""
from app.core.pdf_lienzo import RegistroFormatos
from app.modules.tte.formats.datos import EmpresaImpresion

registro = RegistroFormatos("guía")

FORMATO_POR_DEFECTO = 3


def resolver_formato(formato: int | None, empresa: EmpresaImpresion) -> int:
    """El pedido; si no llega, `codigo_formato_guia_web` de configuración; si no, el 3."""
    return registro.resolver(formato, empresa.codigo_formato_guia_web, FORMATO_POR_DEFECTO)


# Registro de formatos (el orden no importa)
from app.modules.tte.formats.guia import guia1  # noqa: E402,F401
from app.modules.tte.formats.guia import guia2  # noqa: E402,F401
from app.modules.tte.formats.guia import guia3  # noqa: E402,F401
from app.modules.tte.formats.guia import guia4  # noqa: E402,F401

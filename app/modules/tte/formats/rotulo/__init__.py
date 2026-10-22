"""
Formatos de impresión de rótulos (una etiqueta por unidad de la guía).

Para agregar un formato: crear `rotuloN.py` con la clase `RotuloN(FormatoPdf)` decorada con
`@registro.registrar` e importarlo al final de este archivo. La ruta y el motor no cambian.
"""
from app.core.pdf_lienzo import RegistroFormatos
from app.modules.tte.formats.datos import EmpresaImpresion

registro = RegistroFormatos("rótulo")

FORMATO_POR_DEFECTO = 1


def resolver_formato(formato: int | None, empresa: EmpresaImpresion) -> int:
    """El pedido; si no llega, `codigo_formato_rotulo` de configuración; si no, el 1."""
    return registro.resolver(formato, empresa.codigo_formato_rotulo, FORMATO_POR_DEFECTO)


def piezas(unidades: float) -> int:
    """Rótulos que lleva una guía: uno por unidad, mínimo uno."""
    return max(int(unidades or 0), 1)


# Registro de formatos (el orden no importa)
from app.modules.tte.formats.rotulo import rotulo1  # noqa: E402,F401
from app.modules.tte.formats.rotulo import rotulo2  # noqa: E402,F401

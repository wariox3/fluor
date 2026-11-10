"""
Formato PDF de la autorización para portar armas.

Port de `App\\Formato\\RecursoHumano\\AutorizacionArma` de holmio, dibujado con `Lienzo` (mm,
origen arriba a la izquierda, primitivas tipo FPDF). Una página por empleado con:
- las imágenes del encabezado del formato (`gen_formato_imagen`), en su posición;
- el texto del formato 14 (`gen_formato.contenido`) con sus marcadores `#1`…`#a` reemplazados;
- la tabla de armas del polígono del empleado (arma | CALIBRE | calibre mm);
- "Esta autorización de armas es otorgada por:" y hasta tres firmas del formato;
- "Página X de Y" en el pie (a 272 mm: en holmio quedaba fuera de la hoja).

Si el texto no cabe en la página, sigue en la siguiente (holmio lo hacía con el salto
automático de FPDF).
"""

from dataclasses import dataclass, field
from datetime import date

from reportlab.lib.pagesizes import letter

from app.core.pdf_lienzo import Lienzo
from app.core.utils import fecha_larga, fmt_cantidad

# Página carta con los márgenes de holmio: 25 mm a los lados y salto de página a 20 mm del pie
_MARGEN_X = 25.0
_ANCHO_TEXTO = 215.9 - 2 * _MARGEN_X
_INICIO_TEXTO = 42.0
_FIN_PAGINA = 259.0
_ALTO_LINEA = 5.0

# Posiciones fijas de las firmas en holmio (mm)
_Y_LINEA_FIRMA = 223.0
_FIRMAS_X = (26.0, 90.0, 150.0)
# Holmio lo dibuja a 290 mm, fuera de la hoja carta (279 mm), y nunca se veía
_Y_PIE = 272.0


@dataclass
class DatosEmpleado:
    """Lo que el formato imprime de cada empleado."""

    nombre: str
    identificacion: str
    cargo: str
    fecha_desde_contrato: date | None
    # (nombre del arma, calibre en mm)
    armas: list[tuple[str, float | None]] = field(default_factory=list)


@dataclass
class DatosEmpresa:
    nombre: str
    direccion: str
    correo: str
    ciudad: str
    nit: str


def _reemplazar(contenido: str, empleado: DatosEmpleado, empresa: DatosEmpresa, hoy: date) -> str:
    """Marcadores del formato 14, en el mismo orden en que los reemplaza holmio."""
    valores = {
        "#1": empleado.nombre,
        "#2": empleado.identificacion,
        "#3": empleado.cargo,
        "#4": fecha_larga(hoy),
        "#5": empresa.nombre,
        "#6": empresa.direccion,
        "#7": empresa.correo,
        "#8": empresa.ciudad,
        "#9": empresa.nit,
        "#a": empleado.fecha_desde_contrato.strftime("%Y-%m-%d") if empleado.fecha_desde_contrato else "",
    }
    for marcador, valor in valores.items():
        contenido = contenido.replace(marcador, valor or "")
    return contenido.replace("\r\n", "\n")


def _firmas(formato) -> list[tuple[str, str]]:
    """Firmas configuradas en el formato: la principal siempre; las otras dos si tienen nombre."""
    firmas = [(formato.nombre_firma or "", formato.cargo_firma or "")]
    if formato.nombre_firma_otro:
        firmas.append((formato.nombre_firma_otro, formato.cargo_firma_otro or ""))
    if formato.nombre_firma_otro_dos:
        firmas.append((formato.nombre_firma_otro_dos, formato.cargo_firma_otro_dos or ""))
    return firmas


class _Documento:
    """Arma el PDF en dos pasadas: primero cuenta las páginas, luego dibuja con el total."""

    def __init__(self, formato, imagenes, empresa: DatosEmpresa, hoy: date):
        self.formato = formato
        self.imagenes = [img for img in imagenes if img.imagen]
        self.empresa = empresa
        self.hoy = hoy
        self.total = 0
        self.lienzo = Lienzo(letter)

    def _nueva_pagina(self, dibujar: bool) -> None:
        self.pagina += 1
        if not dibujar:
            return
        self.lienzo.nueva_pagina()
        for img in self.imagenes:
            self.lienzo.imagen(img.imagen, img.posicion_x or 0, img.posicion_y or 0, img.ancho or 0, img.alto or 0)
        self.lienzo.fuente(8)
        self.lienzo.texto(170, _Y_PIE, f"Página {self.pagina} de {self.total}")
        self.lienzo.fuente(11)

    def _empleado(self, empleado: DatosEmpleado, dibujar: bool) -> None:
        lienzo = self.lienzo
        self._nueva_pagina(dibujar)
        lienzo.fuente(11)

        y = _INICIO_TEXTO
        texto = _reemplazar(self.formato.contenido or "", empleado, self.empresa, self.hoy)
        for parrafo in texto.split("\n"):
            # Un párrafo vacío es una línea en blanco, como en el MultiCell de FPDF
            for linea in lienzo.partir(parrafo, _ANCHO_TEXTO - 2 * Lienzo.MARGEN_CELDA) or [""]:
                if y + _ALTO_LINEA > _FIN_PAGINA:
                    self._nueva_pagina(dibujar)
                    lienzo.fuente(11)
                    y = _INICIO_TEXTO
                if dibujar:
                    lienzo.celda(_MARGEN_X, y, _ANCHO_TEXTO, _ALTO_LINEA, linea)
                y += _ALTO_LINEA
        y += 5

        # Armas del polígono: nombre | CALIBRE | calibre mm
        for nombre, calibre in empleado.armas:
            if y + 8 > _FIN_PAGINA:
                self._nueva_pagina(dibujar)
                y = _INICIO_TEXTO
            if dibujar:
                lienzo.fuente(10, negrita=True)
                lienzo.celda(_MARGEN_X, y, 50, 8, nombre, borde=1, alinear="C")
                lienzo.fuente(10)
                lienzo.celda(_MARGEN_X + 50, y, 50, 8, "CALIBRE", borde=1, alinear="C")
                lienzo.celda(_MARGEN_X + 100, y, 50, 8, f"{fmt_cantidad(calibre)} mm", borde=1, alinear="C")
            y += 8

        # Holmio deja 50 mm y fija las firmas en 223 mm; si el texto ya pasó de ahí, van en otra página
        y_otorgada = y + 50
        if y_otorgada + 4 > _Y_LINEA_FIRMA - 5:
            self._nueva_pagina(dibujar)
            y_otorgada = _INICIO_TEXTO + 50
        if not dibujar:
            return
        lienzo.fuente(11)
        lienzo.celda(_MARGEN_X, y_otorgada, 70, 4, "Esta autorización de armas es otorgada por:")
        for x, (nombre, cargo) in zip(_FIRMAS_X, _firmas(self.formato)):
            lienzo.celda(x, _Y_LINEA_FIRMA, 50, 4, "", borde="B")
            lienzo.celda(x - 1, _Y_LINEA_FIRMA + 5, 60, 4, nombre)
            lienzo.multicelda(x - 1, _Y_LINEA_FIRMA + 9, 50, 4, cargo)

    def generar(self, empleados: list[DatosEmpleado]) -> bytes:
        # Primera pasada: solo cuenta páginas, para el "Página X de Y"
        self.pagina = 0
        for empleado in empleados:
            self._empleado(empleado, dibujar=False)
        self.total = self.pagina

        self.pagina = 0
        for empleado in empleados:
            self._empleado(empleado, dibujar=True)
        return self.lienzo.terminar()


def generar(empleados: list[DatosEmpleado], formato, imagenes, empresa: DatosEmpresa, hoy: date | None = None) -> bytes:
    """PDF con una autorización por empleado, en el orden recibido."""
    return _Documento(formato, imagenes, empresa, hoy or date.today()).generar(empleados)

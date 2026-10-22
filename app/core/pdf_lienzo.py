"""
Base para formatos PDF dibujados por coordenadas (guías, rótulos, etc.).

- `Lienzo`: envuelve el canvas de ReportLab con medidas en mm y origen arriba a la
  izquierda. Sus primitivas (`celda`, `multicelda`, `texto`, `rect`…) se comportan como
  las de FPDF, así un formato de holmio se migra casi línea por línea.
- `FormatoPdf`: clase base de cada formato.
- `RegistroFormatos`: catálogo de formatos de un tipo de documento y motor que los genera.
"""
import re
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable, Union

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import createBarcodeDrawing, qrencoder
from reportlab.graphics.barcode.code128 import _patterns as _PATRONES_CODE128
from reportlab.graphics.shapes import Drawing, Group
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

OrigenImagen = Union[bytes, str, Path, ImageReader, None]

_PT_POR_MM = 72 / 25.4


class Lienzo:
    """Canvas en mm con origen superior izquierdo y primitivas tipo FPDF."""

    MARGEN_CELDA = 1.0  # mm; igual al cMargin por defecto de FPDF

    def __init__(self, tamano: tuple[float, float]):
        self._buffer = BytesIO()
        self.canvas = Canvas(self._buffer, pagesize=tamano)
        self.ancho, self.alto = tamano[0] / mm, tamano[1] / mm
        self._paginas = 0
        self._fuente = "Helvetica"
        self._tamano_fuente = 10.0
        self._color_texto = (0, 0, 0)

    # ── Páginas ───────────────────────────────────────────────────────────────

    def nueva_pagina(self) -> None:
        if self._paginas:
            self.canvas.showPage()
        self._paginas += 1
        self.canvas.setLineWidth(0.2 * mm)  # grosor de línea por defecto de FPDF
        self._aplicar_fuente()
        self.color_texto(*self._color_texto)

    def terminar(self) -> bytes:
        self.canvas.save()
        return self._buffer.getvalue()

    # ── Estado ────────────────────────────────────────────────────────────────

    def fuente(self, tamano: float, negrita: bool = False) -> None:
        self._fuente = "Helvetica-Bold" if negrita else "Helvetica"
        self._tamano_fuente = tamano
        self._aplicar_fuente()

    def _aplicar_fuente(self) -> None:
        self.canvas.setFont(self._fuente, self._tamano_fuente)

    def color_texto(self, r: int, g: int, b: int) -> None:
        self._color_texto = (r, g, b)
        self.canvas.setFillColorRGB(r / 255, g / 255, b / 255)

    def grosor_linea(self, grosor_mm: float) -> None:
        self.canvas.setLineWidth(grosor_mm * mm)

    def ancho_texto(self, texto: str) -> float:
        """Ancho en mm del texto con la fuente actual."""
        return stringWidth(texto, self._fuente, self._tamano_fuente) / mm

    def ajustar(self, texto: Any, ancho: float) -> str:
        """Recorta el texto para que quepa en `ancho` mm con la fuente actual."""
        texto = _texto(texto)
        if self.ancho_texto(texto) <= ancho:
            return texto
        while texto and self.ancho_texto(texto) > ancho:
            texto = texto[:-1]
        return texto.rstrip()

    # ── Texto ─────────────────────────────────────────────────────────────────

    def _y(self, y: float) -> float:
        return (self.alto - y) * mm

    def texto(self, x: float, y: float, texto: Any) -> None:
        """Texto con la línea base en (x, y), como `Text()` de FPDF."""
        self.canvas.drawString(x * mm, self._y(y), _texto(texto))

    def texto_rotado(self, x: float, y: float, texto: Any, angulo: float) -> None:
        self.canvas.saveState()
        self.canvas.translate(x * mm, self._y(y))
        self.canvas.rotate(angulo)
        self.canvas.drawString(0, 0, _texto(texto))
        self.canvas.restoreState()

    def celda(self, x: float, y: float, w: float, h: float, texto: Any = "",
              borde: Union[int, str] = 0, alinear: str = "L",
              relleno: tuple[int, int, int] | None = None) -> None:
        """Equivale a `SetXY(x, y)` + `Cell(w, h, texto, borde, 0, alinear, relleno)` de FPDF."""
        if relleno:
            self.rect(x, y, w, h, relleno=relleno, borde=False)
        self._bordes(x, y, w, h, borde)
        texto = _texto(texto)
        if not texto:
            return
        ancho = self.ancho_texto(texto)
        if alinear == "R":
            tx = x + w - self.MARGEN_CELDA - ancho
        elif alinear == "C":
            tx = x + (w - ancho) / 2
        else:
            tx = x + self.MARGEN_CELDA
        tamano_mm = self._tamano_fuente / _PT_POR_MM
        self.texto(tx, y + h / 2 + 0.3 * tamano_mm, texto)

    def multicelda(self, x: float, y: float, w: float, h: float, texto: Any,
                   alinear: str = "L", max_lineas: int | None = None) -> int:
        """Texto con salto de línea dentro de `w` mm, una celda de alto `h` por línea.

        Devuelve la cantidad de líneas dibujadas.
        """
        lineas = self.partir(texto, w - 2 * self.MARGEN_CELDA)
        if max_lineas is not None:
            lineas = lineas[:max_lineas]
        for i, linea in enumerate(lineas):
            self.celda(x, y + i * h, w, h, linea, alinear=alinear)
        return len(lineas)

    def partir(self, texto: Any, ancho: float) -> list[str]:
        """Parte el texto en líneas que caben en `ancho` mm (palabras largas por caracteres)."""
        lineas: list[str] = []
        for parrafo in _texto(texto).split("\n"):
            actual = ""
            for palabra in parrafo.split():
                candidata = f"{actual} {palabra}".strip()
                if self.ancho_texto(candidata) <= ancho:
                    actual = candidata
                    continue
                if actual:
                    lineas.append(actual)
                while self.ancho_texto(palabra) > ancho:
                    corte = len(self.ajustar(palabra, ancho)) or 1
                    lineas.append(palabra[:corte])
                    palabra = palabra[corte:]
                actual = palabra
            lineas.append(actual)
        return [linea for linea in lineas if linea]

    # ── Figuras ───────────────────────────────────────────────────────────────

    def rect(self, x: float, y: float, w: float, h: float,
             relleno: tuple[int, int, int] | None = None, borde: bool = True) -> None:
        if relleno:
            self.canvas.saveState()
            self.canvas.setFillColorRGB(*(c / 255 for c in relleno))
        self.canvas.rect(x * mm, self._y(y + h), w * mm, h * mm,
                         stroke=1 if borde else 0, fill=1 if relleno else 0)
        if relleno:
            self.canvas.restoreState()

    def linea(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.canvas.line(x1 * mm, self._y(y1), x2 * mm, self._y(y2))

    def _bordes(self, x: float, y: float, w: float, h: float, borde: Union[int, str]) -> None:
        if not borde:
            return
        if borde == 1:
            self.rect(x, y, w, h)
            return
        if "L" in borde:
            self.linea(x, y, x, y + h)
        if "T" in borde:
            self.linea(x, y, x + w, y)
        if "R" in borde:
            self.linea(x + w, y, x + w, y + h)
        if "B" in borde:
            self.linea(x, y + h, x + w, y + h)

    # ── Imágenes y códigos ────────────────────────────────────────────────────

    def imagen(self, origen: OrigenImagen, x: float, y: float, w: float, h: float) -> bool:
        """Dibuja la imagen estirada a w×h mm (como FPDF). Devuelve False si no se pudo."""
        lector = imagen_lector(origen)
        if lector is None:
            return False
        try:
            self.canvas.drawImage(lector, x * mm, self._y(y + h), w * mm, h * mm, mask="auto")
            return True
        except Exception:
            return False

    def qr(self, valor: Any, x: float, y: float, tamano: float,
           lado_px: int = 300, margen_px: int = 10) -> None:
        """QR con la misma geometría que endroid/qr-code en holmio (300 px + margen de 10 px).

        Los módulos ocupan `lado_px // n * n` px centrados en `lado_px + 2 * margen_px` px, sobre
        fondo blanco, y se dibujan por tramos horizontales para que no queden líneas entre ellos.
        """
        codigo = _qr_como_holmio(_texto(valor))
        n = codigo.getModuleCount()
        total_px = lado_px + 2 * margen_px
        modulo = (lado_px // n) * tamano / total_px
        inicio = (total_px - (lado_px // n) * n) / 2 * tamano / total_px

        self.rect(x, y, tamano, tamano, relleno=(255, 255, 255), borde=False)
        self.canvas.saveState()
        self.canvas.setFillColorRGB(0, 0, 0)
        for fila in range(n):
            columna = 0
            while columna < n:
                if not codigo.isDark(fila, columna):
                    columna += 1
                    continue
                desde = columna
                while columna < n and codigo.isDark(fila, columna):
                    columna += 1
                self.canvas.rect((x + inicio + desde * modulo) * mm, self._y(y + inicio + (fila + 1) * modulo),
                                 (columna - desde) * modulo * mm, modulo * mm, stroke=0, fill=1)
        self.canvas.restoreState()

    def codigo_barras(self, valor: Any, x: float, y: float, w: float, h: float,
                      tipo: str = "Standard39") -> None:
        """Código de barras estirado para ocupar exactamente w×h mm.

        Como picqer en holmio: sin márgenes en blanco; en Code39 las barras anchas miden 3 veces la
        angosta y en Code128 los juegos de caracteres se eligen con la misma regla de picqer.
        """
        if tipo == "Code128":
            self._code128(_texto(valor), x, y, w, h)
            return
        opciones = {"checksum": 0, "ratio": 3.0} if tipo == "Standard39" else {}
        barras = createBarcodeDrawing(tipo, value=_texto(valor), barHeight=h * mm, barWidth=1.0,
                                      humanReadable=False, quiet=0, **opciones)
        grupo = Group(barras)
        grupo.transform = ((w * mm) / barras.width if barras.width else 1, 0, 0, 1, 0, 0)
        dibujo = Drawing(w * mm, h * mm)
        dibujo.add(grupo)
        renderPDF.draw(dibujo, self.canvas, x * mm, self._y(y + h))


    def _code128(self, valor: str, x: float, y: float, w: float, h: float) -> None:
        # Patrón de cada código: mayúsculas = barra, minúsculas = espacio; A/a = 1 módulo … D/d = 4
        anchos = [(letra.isupper(), ord(letra.lower()) - ord("a") + 1)
                  for codigo in _codigos_code128(valor) for letra in _PATRONES_CODE128[codigo]]
        modulo = w / sum(ancho for _, ancho in anchos)
        self.canvas.saveState()
        self.canvas.setFillColorRGB(0, 0, 0)
        posicion = x
        for es_barra, ancho in anchos:
            if es_barra:
                self.canvas.rect(posicion * mm, self._y(y + h), ancho * modulo * mm, h * mm, stroke=0, fill=1)
            posicion += ancho * modulo
        self.canvas.restoreState()


def _codigos_code128(valor: str) -> list[int]:
    """Códigos Code128 (inicio, datos, control y parada) con la regla automática de picqer.

    Las corridas de 4 o más dígitos van en el juego C (si son impares, el primer dígito queda
    en B) y el resto en el juego B.
    """
    secuencias: list[tuple[str, str]] = []
    fin = 0
    for corrida in re.finditer(r"[0-9]{4,}", valor):
        inicio, digitos = corrida.start(), corrida.group()
        if len(digitos) % 2:
            inicio, digitos = inicio + 1, digitos[1:]
        if inicio > fin:
            secuencias.append(("B", valor[fin:inicio]))
        secuencias.append(("C", digitos))
        fin = inicio + len(digitos)
    if fin < len(valor):
        secuencias.append(("B", valor[fin:]))

    codigos: list[int] = []
    for i, (juego, texto) in enumerate(secuencias):
        if i == 0:
            codigos.append(105 if juego == "C" else 104)
        elif secuencias[i - 1][0] != juego:
            codigos.append(99 if juego == "C" else 100)
        if juego == "C":
            codigos += [int(texto[k:k + 2]) for k in range(0, len(texto), 2)]
        else:
            codigos += [ord(caracter) - 32 for caracter in texto]
    control = sum(codigo * max(i, 1) for i, codigo in enumerate(codigos)) % 103
    return codigos + [control, 106]


def imagen_lector(origen: OrigenImagen) -> ImageReader | None:
    """Convierte bytes, ruta o ImageReader en un ImageReader reutilizable (None si falla)."""
    if origen is None or origen == b"":
        return None
    if isinstance(origen, ImageReader):
        return origen
    try:
        if isinstance(origen, (bytes, bytearray, memoryview)):
            return ImageReader(BytesIO(bytes(origen)))
        ruta = Path(origen)
        return ImageReader(str(ruta)) if ruta.is_file() else None
    except Exception:
        return None


def _qr_como_holmio(valor: str) -> qrencoder.QRCode:
    """Matriz QR (corrección L) con la máscara que elegiría bacon-qr-code en holmio.

    ReportLab elige la máscara con otro cálculo; el QR se lee igual, pero así queda idéntico.
    """
    codigo = qrencoder.QRCode(None, qrencoder.QRErrorCorrectLevel.L)
    codigo.addData(valor)
    codigo.make()  # fija la versión
    penalizaciones = []
    for mascara in range(8):
        codigo.makeImpl(False, mascara)
        matriz = [[bool(codigo.isDark(f, c)) for c in range(codigo.getModuleCount())]
                  for f in range(codigo.getModuleCount())]
        penalizaciones.append(_penalizacion_qr(matriz))
    codigo.makeImpl(False, penalizaciones.index(min(penalizaciones)))
    return codigo


def _penalizacion_qr(m: list[list[bool]]) -> int:
    """Reglas de penalización N1–N4 de la norma QR, tal como las implementa bacon-qr-code."""
    n = len(m)
    columnas = [[m[f][c] for f in range(n)] for c in range(n)]
    total = 0
    for linea in m + columnas:  # N1: tramos de 5 o más módulos iguales
        tramo, previo = 0, None
        for valor in linea:
            if valor == previo:
                tramo += 1
            else:
                if tramo >= 5:
                    total += 3 + tramo - 5
                tramo, previo = 1, valor
        if tramo >= 5:
            total += 3 + tramo - 5
    total += 3 * sum(  # N2: bloques de 2×2 del mismo color
        1 for f in range(n - 1) for c in range(n - 1)
        if m[f][c] == m[f][c + 1] == m[f + 1][c] == m[f + 1][c + 1]
    )
    patron = [True, False, True, True, True, False, True]

    for linea in m + columnas:  # N3: patrón 1:1:3:1:1 con 4 módulos claros (dentro de la matriz) a un lado
        for i in range(n - 6):
            if linea[i:i + 7] != patron:
                continue
            despues = i + 10 < n and not any(linea[i + 7:i + 11])
            antes = i - 4 >= 0 and not any(linea[i - 4:i])
            if despues or antes:
                total += 40
    oscuros = sum(map(sum, m))  # N4: proporción de módulos oscuros
    total += int(abs(oscuros / (n * n) - 0.5) * 20) * 10
    return total


def _texto(valor: Any) -> str:
    return "" if valor is None else str(valor)


class FormatoPdf:
    """Clase base de un formato. Cada formato define su código, nombre, tamaño y dibujo."""

    codigo: int
    nombre: str
    tamano: tuple[float, float]

    def paginas(self, documento: Any) -> int:
        """Páginas que ocupa un documento (un rótulo, por ejemplo, ocupa una por unidad)."""
        return 1

    def dibujar(self, lienzo: Lienzo, documento: Any, contexto: Any, pagina: int) -> None:
        raise NotImplementedError


class RegistroFormatos:
    """Catálogo de formatos de un tipo de documento y generador del PDF."""

    def __init__(self, documento: str):
        self.documento = documento
        self._formatos: dict[int, FormatoPdf] = {}

    def registrar(self, clase: type[FormatoPdf]) -> type[FormatoPdf]:
        """Decorador: `@registro.registrar` sobre la clase del formato."""
        formato = clase()
        if formato.codigo in self._formatos:
            raise ValueError(f"El formato {formato.codigo} de {self.documento} ya está registrado")
        self._formatos[formato.codigo] = formato
        return clase

    def existe(self, codigo: int | None) -> bool:
        return codigo in self._formatos

    def obtener(self, codigo: int) -> FormatoPdf:
        formato = self._formatos.get(codigo)
        if formato is None:
            disponibles = ", ".join(str(c) for c in sorted(self._formatos))
            raise ValueError(f"El formato {codigo} de {self.documento} no existe. Disponibles: {disponibles}")
        return formato

    def resolver(self, pedido: int | None, configurado: str | None, por_defecto: int) -> int:
        """Formato pedido; si no llega, el configurado; si tampoco es válido, el por defecto.

        Un formato pedido explícitamente que no existe es un error (ValueError).
        """
        if pedido is not None:
            self.obtener(pedido)
            return pedido
        configurado = (configurado or "").strip()
        if configurado.isdigit() and self.existe(int(configurado)):
            return int(configurado)
        return por_defecto

    def listar(self) -> list[FormatoPdf]:
        return [self._formatos[c] for c in sorted(self._formatos)]

    def generar(self, codigo: int, documentos: Iterable[Any], contexto: Any = None) -> bytes:
        formato = self.obtener(codigo)
        lienzo = Lienzo(formato.tamano)
        for documento in documentos:
            for pagina in range(1, formato.paginas(documento) + 1):
                lienzo.nueva_pagina()
                formato.dibujar(lienzo, documento, contexto, pagina)
        return lienzo.terminar()

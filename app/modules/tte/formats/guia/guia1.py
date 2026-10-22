"""
Guía formato 1 — A4 con 4 copias iguales por hoja.
Réplica de holmio `src/Formato/Transporte/Guia1.php`; las coordenadas son las mismas (mm).
"""
from reportlab.lib.pagesizes import A4

from app.core.pdf_lienzo import FormatoPdf, Lienzo, imagen_lector
from app.modules.tte.formats.datos import EmpresaImpresion, GuiaImpresion, numero
from app.modules.tte.formats.guia import registro

_BLANCO = (255, 255, 255)
_COPIAS = [20, 88, 156, 224]  # y de referencia de cada copia


@registro.registrar
class Guia1(FormatoPdf):
    codigo = 1
    nombre = "A4 con 4 copias por hoja"
    tamano = A4

    def dibujar(self, l: Lienzo, guia: GuiaImpresion, empresa: EmpresaImpresion, pagina: int) -> None:
        logo = imagen_lector(empresa.logo)
        for y in _COPIAS:
            self._copia(l, guia, empresa, y, logo)

    def _copia(self, l: Lienzo, g: GuiaImpresion, e: EmpresaImpresion, y: float, logo) -> None:
        l.imagen(logo, 10, y - 16, 40, 15)
        l.codigo_barras(g.codigo, 165, y - 10, 33, 10)

        l.fuente(12, negrita=True)
        l.celda(168, y - 15, 30, 4, g.codigo, alinear="R")
        l.fuente(8)
        l.texto(55, y - 13, e.nombre)
        l.texto(55, y - 9, f"{e.nit}-{e.digito_verificacion}")
        l.texto(55, y - 5, e.direccion)
        l.texto(55, y - 1, e.telefono)

        # Pares (título, valor) que comparten caja: el valor tapa el borde derecho del título y, como
        # en holmio, un valor largo queda tapado por el fondo blanco de la celda siguiente.
        # (dy, x título, ancho, título, x valor, valor, tamaño de letra del valor)
        fecha = g.fecha_ingreso.strftime("%Y-%m-%d") if g.fecha_ingreso else ""
        for dy, x, ancho, titulo, x_valor, valor, tamano in [
            (0, 10, 49, "Fecha:", 22, fecha, 8),
            (0, 71, 47, "Origen:", 84, g.ciudad_origen_nombre, 8),
            (0, 131, 47, "Destino:", 151, g.ciudad_destino_nombre, 8),
            (6, 10, 49, "Remite:", 22, g.remitente_nombre, 8),
            (6, 71, 77, "Direccion:", 87, g.tercero_direccion, 8),
            (6, 161, 23, "Tel:", 175, g.tercero_telefono, 8),
            (12, 10, 49, "Destinatario:", 28, g.destinatario_nombre, 8),
            (12, 71, 77, "Direccion:", 87, g.destinatario_direccion[:60], 7),
            (12, 161, 23, "Tel:", 175, g.destinatario_telefono, 8),
        ]:
            l.fuente(8, negrita=True)
            l.celda(x, y + dy, ancho, 6, titulo, borde="TLB", relleno=_BLANCO)
            l.fuente(tamano)
            l.celda(x_valor, y + dy, ancho, 6, valor, borde="TRB", relleno=_BLANCO)

        l.fuente(8, negrita=True)
        l.celda(10, y + 18, 43, 6, "Tipo cobro:", borde="TL", relleno=_BLANCO)
        l.fuente(8)
        l.celda(28, y + 18, 43, 6, g.tipo_nombre, borde="TR", relleno=_BLANCO)
        l.fuente(8, negrita=True)
        l.celda(10, y + 24, 43, 6, "Documento:", borde="LB", relleno=_BLANCO)
        l.fuente(8)
        l.celda(28, y + 24, 43, 6, g.documento_cliente, borde="RB", relleno=_BLANCO)

        l.fuente(7.8, negrita=True)
        l.multicelda(71.5, y + 19, 128, 3.5, f"Observaciones:{g.comentario}", max_lineas=3)
        l.celda(71, y + 18, 127, 12, "", borde=1)

        # ── Liquidación ───────────────────────────────────────────────────────
        l.fuente(8, negrita=True)
        for x, ancho, titulo, borde in [
            (10, 20, "Cant", "TLB"), (20, 20, "Peso", "TB"), (32, 20, "Vol", "TB"),
            (45, 20, "Flete", "TB"), (60, 20, "Manejo", "TB"), (80, 20, "Cobro", "TB"),
            (95, 40, "Declarado", "TB"), (130, 68, "DEVOLVER FIRMADO Y SELLADO", "TBR"),
        ]:
            l.celda(x, y + 30, ancho, 6, titulo, borde=borde, relleno=_BLANCO)

        vr_flete, vr_manejo = self._valores(g)
        l.fuente(8)
        for x, ancho, valor, borde in [
            (10, 20, g.unidades, "TL"), (20, 20, g.peso_real, "T"), (32, 20, g.peso_volumen, "T"),
            (45, 20, vr_flete, "T"), (60, 20, vr_manejo, "T"), (80, 20, g.vr_cobro_entrega, "T"),
            (95, 40, g.vr_declara, "T"),
        ]:
            l.celda(x, y + 36, ancho, 6, numero(valor), borde=borde, relleno=_BLANCO)
        l.fuente(8, negrita=True)
        l.celda(115, y + 36, 83, 6, "NOMBRE", borde="TLR", relleno=_BLANCO)

        l.fuente(8)
        for x, ancho, borde in [(10, 20, "LB"), (25, 20, "B"), (45, 20, "B"), (60, 20, "B"), (80, 20, "B"), (95, 40, "B")]:
            l.celda(x, y + 42, ancho, 6, "", borde=borde, relleno=_BLANCO)
        l.fuente(8, negrita=True)
        l.celda(115, y + 42, 83, 6, "CC NIT.                                                       FECHA HORA",
                borde="LBR", relleno=_BLANCO)

    @staticmethod
    def _valores(g: GuiaImpresion) -> tuple[float, float]:
        """Flete y manejo con la regla de Guia1: se ocultan si el cliente lo pide en crédito sin factura."""
        if not g.factura and g.tercero_ocultar_valores and g.codigo_pago == "COR":
            return 0, 0
        return g.vr_flete, g.vr_manejo

"""
Rótulo formato 2 — etiqueta pequeña 50×20 mm, una por unidad.
Réplica de holmio `src/Formato/Transporte/Rotulo2.php`; las coordenadas son las mismas (mm).
"""
from reportlab.lib.units import mm

from app.core.pdf_lienzo import FormatoPdf, Lienzo
from app.core.utils import fmt_cantidad
from app.modules.tte.formats.datos import EmpresaImpresion, GuiaImpresion, numero
from app.modules.tte.formats.rotulo import piezas, registro

_QR_X = 39  # mm; los textos de la izquierda no deben pisar el QR


@registro.registrar
class Rotulo2(FormatoPdf):
    codigo = 2
    nombre = "Etiqueta 50×20 mm"
    tamano = (50 * mm, 20 * mm)

    def paginas(self, guia: GuiaImpresion) -> int:
        return piezas(guia.unidades)

    def dibujar(self, l: Lienzo, g: GuiaImpresion, e: EmpresaImpresion, pagina: int) -> None:
        l.qr(g.codigo, _QR_X, 5, 10)

        l.fuente(5, negrita=True)
        l.texto(2, 3, f"GUIA No. {g.codigo}")
        l.fuente(6, negrita=True)
        l.texto(2, 5.5, "DOC CLIENTE:")
        l.fuente(6)
        l.texto(18, 5.5, l.ajustar(g.documento_cliente[:16], _QR_X - 18))

        # (rótulo, x del rótulo, x del valor, y, valor)
        for rotulo, x_valor, y, valor in [
            ("DESTINATARIO:", 14, 8, g.destinatario_nombre[:24]),
            ("DIRECCIÓN:", 11, 10, g.destinatario_direccion[:24]),
            ("DESTINO:", 9, 12, g.ciudad_destino_nombre),
            ("REMITENTE:", 11, 14, g.remitente_nombre[:24]),
        ]:
            l.fuente(4, negrita=True)
            l.texto(2, y, rotulo)
            l.fuente(4)
            l.texto(x_valor, y, l.ajustar(valor, _QR_X - x_valor))

        l.fuente(4, negrita=True)
        l.texto(2, 18, "ZONA")
        l.texto(2, 19.5, l.ajustar(g.franja, 8))  # holmio usa y=19 y se monta sobre "ZONA"
        l.texto(11, 18, f"PIEZA {pagina} / {fmt_cantidad(g.unidades)}")
        if g.vr_cobro_entrega > 0:
            l.fuente(5, negrita=True)
            l.texto(39, 18, f"${numero(g.vr_cobro_entrega)}")

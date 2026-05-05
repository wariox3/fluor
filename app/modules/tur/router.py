from fastapi import APIRouter
from .routes import programacion
from .routes import programacion_reporte
from .routes import programacion_reporte_tipo
from .routes import programacion_reporte_respuesta
from .routes import turno
from .routes import pedido
from .routes import pedido_detalle
from .routes import consigna
from .routes import factura

router = APIRouter(
    prefix="/tur"
)

router.include_router(programacion.router,prefix="/programacion",tags=["Turno / Programacion"])
router.include_router(programacion_reporte.router,prefix="/programacion_reporte",tags=["Turno / Programacion Reporte"])
router.include_router(programacion_reporte_tipo.router,prefix="/programacion_reporte_tipo",tags=["Turno / Programacion Reporte Tipo"])
router.include_router(programacion_reporte_respuesta.router,prefix="/programacion_reporte_respuesta",tags=["Turno / Programacion Reporte Respuesta"])
router.include_router(turno.router,prefix="/turno",tags=["Turno / Turno"])
router.include_router(pedido.router,prefix="/pedido",tags=["Turno / Pedido"])
router.include_router(pedido_detalle.router,prefix="/pedido_detalle",tags=["Turno / Pedido Detalle"])
router.include_router(consigna.router, prefix="/consigna", tags=["Turno / Consigna"])
router.include_router(factura.router, prefix="/factura", tags=["Turno / Factura"])
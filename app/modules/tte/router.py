from fastapi import APIRouter
from .routes import guia, ciudad, novedad, monitoreo, monitoreo_detalle, seguimiento, producto, empaque, servicio, cliente_condicion, guia_tipo, operacion, zona, despacho, despacho_detalle

router = APIRouter(
    prefix="/tte"
)

router.include_router(guia.router,prefix="/guia",tags=["Transporte y Logística / Guía"])
router.include_router(ciudad.router,prefix="/ciudad",tags=["Transporte y Logística / Ciudad"])
router.include_router(novedad.router,prefix="/novedad",tags=["Transporte y Logística / Novedad"])
router.include_router(monitoreo.router,prefix="/monitoreo",tags=["Transporte y Logística / Monitoreo"])
router.include_router(monitoreo_detalle.router,prefix="/monitoreo-detalle",tags=["Transporte y Logística / Monitoreo Detalle"])
router.include_router(seguimiento.router,prefix="/seguimiento",tags=["Transporte y Logística / Seguimiento"])
router.include_router(producto.router,prefix="/producto",tags=["Transporte y Logística / Producto"])
router.include_router(empaque.router,prefix="/empaque",tags=["Transporte y Logística / Empaque"])
router.include_router(servicio.router,prefix="/servicio",tags=["Transporte y Logística / Servicio"])
router.include_router(cliente_condicion.router,prefix="/cliente-condicion",tags=["Transporte y Logística / Cliente Condición"])
router.include_router(guia_tipo.router,prefix="/guia-tipo",tags=["Transporte y Logística / Guía Tipo"])
router.include_router(operacion.router,prefix="/operacion",tags=["Transporte y Logística / Operación"])
router.include_router(zona.router,prefix="/zona",tags=["Transporte y Logística / Zona"])
router.include_router(despacho.router,prefix="/despacho",tags=["Transporte y Logística / Despacho"])
router.include_router(despacho_detalle.router,prefix="/despacho-detalle",tags=["Transporte y Logística / Despacho Detalle"])
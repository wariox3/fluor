from fastapi import APIRouter
from .routes import guia, ciudad, novedad, monitoreo, monitoreo_detalle, seguimiento, producto, empaque, servicio, cliente_condicion, guia_tipo, operacion, zona, despacho, despacho_detalle, tercero_producto, tercero_operacion, destinatario, condicion, precio_detalle, condicion_flete, condicion_manejo, recibo, movil

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
router.include_router(tercero_producto.router,prefix="/tercero-producto",tags=["Transporte y Logística / Tercero Producto"])
router.include_router(tercero_operacion.router,prefix="/tercero-operacion",tags=["Transporte y Logística / Tercero Operación"])
router.include_router(destinatario.router,prefix="/destinatario",tags=["Transporte y Logística / Destinatario"])
router.include_router(condicion.router,prefix="/condicion",tags=["Transporte y Logística / Condición"])
router.include_router(precio_detalle.router,prefix="/precio-detalle",tags=["Transporte y Logística / Precio Detalle"])
router.include_router(condicion_flete.router,prefix="/condicion-flete",tags=["Transporte y Logística / Condición Flete"])
router.include_router(condicion_manejo.router,prefix="/condicion-manejo",tags=["Transporte y Logística / Condición Manejo"])
router.include_router(recibo.router,prefix="/recibo",tags=["Transporte y Logística / Recibo"])
router.include_router(movil.router,prefix="/movil",tags=["Transporte y Logística / Móvil"])

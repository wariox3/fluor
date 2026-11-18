from fastapi import APIRouter
from .routes import negocio
from .routes import cotizacion, solicitud, solicitud_detalle, solicitud_nuevo, visita

router = APIRouter(
    prefix="/crm"
)

router.include_router(negocio.router,prefix="/negocio", tags=["CRM / Negocio"])
router.include_router(visita.router, prefix="/visita", tags=["CRM / Visita"])
router.include_router(cotizacion.router, prefix="/cotizacion", tags=["CRM / Cotización"])
router.include_router(solicitud.router, prefix="/solicitud", tags=["CRM / Solicitud (PQRS)"])
router.include_router(solicitud_nuevo.router, prefix="/solicitud", tags=["CRM / Solicitud (PQRS)"])
router.include_router(solicitud_detalle.router, prefix="/solicitud", tags=["CRM / Solicitud (PQRS)"])

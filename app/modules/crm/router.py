from fastapi import APIRouter
from .routes import negocio
from .routes import cotizacion, solicitud, visita

router = APIRouter(
    prefix="/crm"
)

router.include_router(negocio.router,prefix="/negocio", tags=["CRM / Negocio"])
router.include_router(visita.router, prefix="/visita", tags=["CRM / Visita"])
router.include_router(cotizacion.router, prefix="/cotizacion", tags=["CRM / Cotización"])
router.include_router(solicitud.router, prefix="/solicitud", tags=["CRM / Solicitud (PQRS)"])

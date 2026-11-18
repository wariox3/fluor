from fastapi import APIRouter
from .routes import cuenta_cobrar
from .routes import movimiento
from .routes import cuenta_cobrar_portal, movimiento_portal

router = APIRouter(
    prefix="/car"
)

router.include_router(cuenta_cobrar.router, prefix="/cuenta-cobrar", tags=["Cartera / Pendiente"])
router.include_router(movimiento.router, prefix="/movimiento", tags=["Cartera / Movimiento"])
router.include_router(cuenta_cobrar_portal.router, prefix="/cuenta-cobrar", tags=["Cartera / Pendiente"])
router.include_router(movimiento_portal.router, prefix="/movimiento", tags=["Cartera / Movimiento"])

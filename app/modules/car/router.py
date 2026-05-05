from fastapi import APIRouter
from .routes import cuenta_cobrar
from .routes import movimiento

router = APIRouter(
    prefix="/car"
)

router.include_router(cuenta_cobrar.router, prefix="/cuenta-cobrar", tags=["Cartera / Pendiente"])
router.include_router(movimiento.router, prefix="/movimiento", tags=["Cartera / Movimiento"])
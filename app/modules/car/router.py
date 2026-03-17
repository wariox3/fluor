from fastapi import APIRouter
from .routes import cuenta_cobrar

router = APIRouter(
    prefix="/car"
)

router.include_router(cuenta_cobrar.router,prefix="/cuenta-cobrar",tags=["Cartera / Pendiente"])
from fastapi import APIRouter
from .routes import empleado

router = APIRouter(
    prefix="/rhu"
)

router.include_router(empleado.router, prefix="/empleado", tags=["Recurso Humano / Empleado"])
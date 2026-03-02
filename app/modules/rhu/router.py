from fastapi import APIRouter
from .routes import empleado

router = APIRouter(
    prefix="/rhu",
    tags=["Recurso Humano"]
)

router.include_router(
    empleado.router,
    prefix="/empleados",
    tags=["Empleados"]
)
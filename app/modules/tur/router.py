from fastapi import APIRouter
from .routes import programacion

router = APIRouter(
    prefix="/tur"
)

router.include_router(programacion.router,prefix="/programacion",tags=["Turno / Programacion"])
from fastapi import APIRouter
from .routes import fichero

router = APIRouter(
    prefix="/doc"
)

router.include_router(fichero.router,prefix="/fichero",tags=["Documental / Fichero"])
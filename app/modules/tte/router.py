from fastapi import APIRouter
from .routes import guia

router = APIRouter(
    prefix="/tte",
    tags=["Transporte y Logística"]
)

router.include_router(guia.router,prefix="/guia",tags=["Guía"])
from fastapi import APIRouter
from .routes import guia

router = APIRouter(
    prefix="/tte"
)

router.include_router(guia.router,prefix="/guia",tags=["Transporte y Logística / Guía"])
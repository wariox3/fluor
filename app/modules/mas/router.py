from fastapi import APIRouter
from .routes import credito_solicitud, configuracion

router = APIRouter(
    prefix="/mas",
    include_in_schema=False,
)

router.include_router(credito_solicitud.router, prefix="/credito-solicitud", tags=["Master / Credito Solicitud"])
router.include_router(configuracion.router, prefix="/configuracion", tags=["Master / Configuracion"])

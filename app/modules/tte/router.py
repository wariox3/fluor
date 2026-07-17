from fastapi import APIRouter
from .routes import guia, ciudad, novedad, monitoreo, monitoreo_detalle, seguimiento

router = APIRouter(
    prefix="/tte"
)

router.include_router(guia.router,prefix="/guia",tags=["Transporte y Logística / Guía"])
router.include_router(ciudad.router,prefix="/ciudad",tags=["Transporte y Logística / Ciudad"])
router.include_router(novedad.router,prefix="/novedad",tags=["Transporte y Logística / Novedad"])
router.include_router(monitoreo.router,prefix="/monitoreo",tags=["Transporte y Logística / Monitoreo"])
router.include_router(monitoreo_detalle.router,prefix="/monitoreo-detalle",tags=["Transporte y Logística / Monitoreo Detalle"])
router.include_router(seguimiento.router,prefix="/seguimiento",tags=["Transporte y Logística / Seguimiento"])
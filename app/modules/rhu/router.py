from fastapi import APIRouter
from .routes import empleado
from .routes import pago
from .routes import pago_tipo
from .routes import pago_detalle
from .routes import contrato
from .routes import reclamo
from .routes import reclamo_concepto

router = APIRouter(
    prefix="/rhu"
)

router.include_router(empleado.router, prefix="/empleado", tags=["Recurso Humano / Empleado"])
router.include_router(pago.router, prefix="/pago", tags=["Recurso Humano / Pago"])
router.include_router(pago_tipo.router, prefix="/pago_tipo", tags=["Recurso Humano / Pago Tipo"])
router.include_router(pago_detalle.router, prefix="/pago_detalle", tags=["Recurso Humano / Pago Detalle"])
router.include_router(contrato.router, prefix="/contrato", tags=["Recurso Humano / Contrato"])
router.include_router(reclamo.router, prefix="/reclamo", tags=["Recurso Humano / Reclamo"])
router.include_router(reclamo_concepto.router, prefix="/reclamo_concepto", tags=["Recurso Humano / Reclamo Concepto"])
from fastapi import APIRouter
from .routes import empleado
from .routes import pago
from .routes import contrato

router = APIRouter(
    prefix="/rhu"
)

router.include_router(empleado.router, prefix="/empleado", tags=["Recurso Humano / Empleado"])
router.include_router(pago.router, prefix="/pago", tags=["Recurso Humano / Pago"])
router.include_router(contrato.router, prefix="/contrato", tags=["Recurso Humano / Contrato"])
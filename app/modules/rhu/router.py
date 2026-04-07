from fastapi import APIRouter
from .routes import empleado
from .routes import pago
from .routes import pago_tipo
from .routes import pago_detalle
from .routes import contrato
from .routes import reclamo
from .routes import reclamo_concepto
from .routes import reclamo_respuesta
from .routes import solicitud_empleado
from .routes import solicitud_empleado_tipo
from .routes import credito
from .routes import embargo
from .routes import adicional
from .routes import concepto
from .routes import capacitacion_detalle
from .routes import empleado_actualizacion

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
router.include_router(reclamo_respuesta.router, prefix="/reclamo_respuesta", tags=["Recurso Humano / Reclamo Respuesta"])
router.include_router(solicitud_empleado.router, prefix="/solicitud_empleado", tags=["Recurso Humano / Solicitud Empleado"])
router.include_router(solicitud_empleado_tipo.router, prefix="/solicitud_empleado_tipo", tags=["Recurso Humano / Solicitud Empleado Tipo"])
router.include_router(credito.router, prefix="/credito", tags=["Recurso Humano / Crédito"])
router.include_router(embargo.router, prefix="/embargo", tags=["Recurso Humano / Embargo"])
router.include_router(adicional.router, prefix="/adicional", tags=["Recurso Humano / Adicional"])
router.include_router(concepto.router, prefix="/concepto", tags=["Recurso Humano / Concepto"])
router.include_router(capacitacion_detalle.router, prefix="/capacitacion_detalle", tags=["Recurso Humano / Capacitacion Detalle"])
router.include_router(empleado_actualizacion.router, prefix="/empleado_actualizacion", tags=["Recurso Humano / Empleado Actualizacion"])
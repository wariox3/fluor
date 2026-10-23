from fastapi import APIRouter
from .routes import credito_solicitud, configuracion, tenant, notificacion, user_tenant, invitacion

router = APIRouter(
    prefix="/mas",
    include_in_schema=False,
)

router.include_router(credito_solicitud.router, prefix="/credito-solicitud", tags=["Master / Credito Solicitud"])
router.include_router(configuracion.router, prefix="/configuracion", tags=["Master / Configuracion"])
router.include_router(tenant.router, prefix="/tenant", tags=["Master / Tenant"])
router.include_router(notificacion.router, prefix="/notificacion", tags=["Master / Notificacion"])
router.include_router(user_tenant.router, prefix="/user-tenant", tags=["Master / User Tenant"])
router.include_router(invitacion.router, prefix="/invitacion", tags=["Master / Invitacion"])

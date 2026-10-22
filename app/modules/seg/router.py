from fastapi import APIRouter

from .routes import usuario_configuracion

router = APIRouter(
    prefix="/seg"
)

router.include_router(usuario_configuracion.router, prefix="/usuario-configuracion", tags=["Seguridad / Usuario Configuración"])

from fastapi import APIRouter
from .routes import seguridad
from .routes import user
from .routes import api_key

router = APIRouter(
    prefix="/auth",
    tags=["seguridad"]
)

router.include_router(seguridad.router,prefix="/seguridad", tags=["Seguridad"])
router.include_router(user.router,prefix="/user", tags=["User"])
router.include_router(api_key.router,prefix="/api-key", tags=["API Key"])
from fastapi import APIRouter
from .routes import prueba
from .routes import ciudad

router = APIRouter(
    prefix="/gen"
)

router.include_router(ciudad.router,prefix="/ciudad", tags=["General / Ciudad"])
router.include_router(prueba.router,prefix="/prueba", tags=["General / Prueba"])
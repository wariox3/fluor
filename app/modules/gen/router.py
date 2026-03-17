from fastapi import APIRouter
from .routes import prueba
from .routes import ciudad
from .routes import tercero
from .routes import item

router = APIRouter(
    prefix="/gen"
)

router.include_router(prueba.router,prefix="/prueba", tags=["General / Prueba"])
router.include_router(ciudad.router,prefix="/ciudad", tags=["General / Ciudad"])
router.include_router(tercero.router,prefix="/tercero", tags=["General / Tercero"])
router.include_router(item.router,prefix="/item", tags=["General / Item"])

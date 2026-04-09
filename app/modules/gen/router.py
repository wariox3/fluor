from fastapi import APIRouter
from .routes import prueba
from .routes import ciudad
from .routes import tercero
from .routes import item
from .routes import formato
from .routes import movimiento
from .routes import movimiento_tipo
from .routes import asesor
from .routes import sucursal
from .routes import enlace
from .routes import formato_imagen

router = APIRouter(
    prefix="/gen"
)

router.include_router(prueba.router,prefix="/prueba", tags=["General / Prueba"])
router.include_router(ciudad.router,prefix="/ciudad", tags=["General / Ciudad"])
router.include_router(tercero.router,prefix="/tercero", tags=["General / Tercero"])
router.include_router(item.router,prefix="/item", tags=["General / Item"])
router.include_router(movimiento.router,prefix="/movimiento", tags=["General / Movimiento"])
router.include_router(movimiento_tipo.router,prefix="/movimiento_tipo", tags=["General / Movimiento Tipo"])
router.include_router(formato.router,prefix="/formato", tags=["General / Formato"])
router.include_router(asesor.router,prefix="/asesor", tags=["General / Asesor"])
router.include_router(sucursal.router,prefix="/sucursal", tags=["General / Sucursal"])
router.include_router(enlace.router,prefix="/enlace", tags=["General / Enlace"])
router.include_router(formato_imagen.router,prefix="/formato-imagen", tags=["General / Formato Imagen"])

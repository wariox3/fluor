from fastapi import APIRouter
from .routes import programacion
from .routes import programacion_reporte
from .routes import programacion_reporte_tipo
from .routes import programacion_reporte_respuesta
from .routes import turno

router = APIRouter(
    prefix="/tur"
)

router.include_router(programacion.router,prefix="/programacion",tags=["Turno / Programacion"])
router.include_router(programacion_reporte.router,prefix="/programacion_reporte",tags=["Turno / Programacion Reporte"])
router.include_router(programacion_reporte_tipo.router,prefix="/programacion_reporte_tipo",tags=["Turno / Programacion Reporte Tipo"])
router.include_router(programacion_reporte_respuesta.router,prefix="/programacion_reporte_respuesta",tags=["Turno / Programacion Reporte Respuesta"])
router.include_router(turno.router,prefix="/turno",tags=["Turno / Turno"])
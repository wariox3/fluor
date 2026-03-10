from fastapi import APIRouter
from .routes import prueba

router = APIRouter(
    prefix="/gen"
)

router.include_router(prueba.router,prefix="/prueba", tags=["General / Prueba"])
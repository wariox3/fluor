from fastapi import APIRouter
from .routes import prueba

router = APIRouter(
    prefix="/gen",
    tags=["General"]
)

router.include_router(prueba.router,prefix="/prueba", tags=["Prueba"])
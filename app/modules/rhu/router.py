from fastapi import APIRouter, Depends, HTTPException
from .routes import empleado
from app.core.security import get_current_user

router = APIRouter(
    prefix="/rhu",
    tags=["Recurso Humano"]
)

router.include_router(
    empleado.router,
    prefix="/empleados",
    tags=["Empleados"]
)
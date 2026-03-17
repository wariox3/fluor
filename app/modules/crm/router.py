from fastapi import APIRouter
from .routes import negocio

router = APIRouter(
    prefix="/crm"
)

router.include_router(negocio.router,prefix="/negocio", tags=["CRM / Negocio"])

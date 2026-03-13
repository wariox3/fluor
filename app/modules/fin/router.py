from fastapi import APIRouter
from .routes import balance

router = APIRouter(
    prefix="/fin"
)

router.include_router(balance.router,prefix="/balance",tags=["Financiero / Balance"])
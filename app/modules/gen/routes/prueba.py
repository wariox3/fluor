from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()

@router.get("/mensaje")
def test(_: dict = Depends(get_current_user)):
    return "Hola mundo desde la ruta de prueba!"
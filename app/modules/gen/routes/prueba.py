import logging
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.zinc import Zinc

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/mensaje")
def test(_: dict = Depends(get_current_user)):
    html_content = f"""
        <h1>¡Hola Mario!</h1>
        <p>Estamos comprometidos con la seguridad de tu cuenta. Por favor verifica tu cuenta haciendo clic en el siguiente enlace.</p>
        <a href='#'>Verificar cuenta</a>
    """
    resultado = Zinc().correo("maestradaz3@gmail.com", "Verifica tu cuenta", html_content)
    return f"Se envió el correo. Status: {resultado['status']}. Datos: {resultado['datos']}"
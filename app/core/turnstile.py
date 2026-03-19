import httpx
from fastapi import HTTPException, status
from app.core.config import TURNSTILE_SECRET_KEY, TURNSTILE_ENABLED

_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v1/siteverify"


def verify_turnstile(token: str) -> None:
    """Verifica un token de Cloudflare Turnstile. Lanza 403 si no es válido."""
    if not TURNSTILE_ENABLED:
        return

    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token de verificación requerido"
        )

    try:
        response = httpx.post(
            _VERIFY_URL,
            data={"secret": TURNSTILE_SECRET_KEY, "response": token},
            timeout=5,
        )
        result = response.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo verificar el token de seguridad"
        )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verificación de seguridad fallida"
        )

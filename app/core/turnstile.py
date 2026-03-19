import logging
import httpx
from fastapi import HTTPException, status
from app.core.config import TURNSTILE_SECRET_KEY, TURNSTILE_ENABLED, DEBUG

logger = logging.getLogger(__name__)

_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def verify_turnstile(token: str | None) -> None:
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
            json={"secret": TURNSTILE_SECRET_KEY, "response": token},
            timeout=10,
            follow_redirects=True,
        )
        result = response.json()
    except httpx.TimeoutException as e:
        logger.error(f"Turnstile timeout: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Timeout verificando token de seguridad"
        )
    except Exception as e:
        logger.error(f"Turnstile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e) if DEBUG else "No se pudo verificar el token de seguridad"
        )

    if not result.get("success"):
        error_codes = result.get("error-codes", [])
        logger.warning(f"Turnstile verification failed: {error_codes}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Verificación fallida: {error_codes}" if DEBUG else "Verificación de seguridad fallida"
        )

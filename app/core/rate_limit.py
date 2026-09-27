import logging
import time
from datetime import datetime, timezone
from threading import Lock

from jose import JWTError, jwt
from limits import parse
from slowapi import Limiter
from sqlalchemy import or_
from starlette.requests import Request

from app.core.config import ALGORITHM, SECRET_KEY
from app.core.master_database import SessionLocal
from app.modules.auth.models.api_key import ApiKey

logger = logging.getLogger(__name__)

# Prefijos de API keys activas, recargados desde la Master DB cada PREFIJOS_TTL segundos.
# Una key recién creada usa el límite por IP hasta la siguiente recarga.
PREFIJOS_TTL = 300
_prefijos_activos: frozenset = frozenset()
_prefijos_cargados_en = 0.0
_prefijos_lock = Lock()


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host


def _get_prefijos_activos() -> frozenset:
    global _prefijos_activos, _prefijos_cargados_en
    if time.monotonic() - _prefijos_cargados_en < PREFIJOS_TTL:
        return _prefijos_activos
    with _prefijos_lock:
        if time.monotonic() - _prefijos_cargados_en < PREFIJOS_TTL:
            return _prefijos_activos
        try:
            with SessionLocal() as db:
                filas = db.query(ApiKey.prefix).filter(
                    ApiKey.is_active == True,
                    or_(ApiKey.expires_at.is_(None), ApiKey.expires_at > datetime.now(timezone.utc)),
                ).all()
            _prefijos_activos = frozenset(fila.prefix for fila in filas)
        except Exception:
            # Si la DB falla se conservan los prefijos anteriores y se reintenta tras el TTL
            logger.warning("No se pudieron recargar los prefijos de API keys para el rate limit", exc_info=True)
        _prefijos_cargados_en = time.monotonic()
        return _prefijos_activos


def _sub_desde_jwt(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
    except JWTError:
        return None


def get_rate_limit_key(request: Request) -> str:
    """Identidad para el rate limit: usuario del JWT, prefijo de API key o IP.

    Solo se usa una identidad verificada (firma del JWT o prefijo activo); si no,
    se cae a la IP para que tokens o prefijos inventados no abran contadores nuevos.
    """
    authorization = request.headers.get("Authorization", "")
    if authorization.lower().startswith("bearer "):
        sub = _sub_desde_jwt(authorization[7:].strip())
        if sub:
            return f"user:{sub}"

    api_key = request.headers.get("X-API-Key")
    if api_key:
        prefijo = api_key.split(".")[0]
        if prefijo in _get_prefijos_activos():
            return f"apikey:{prefijo}"

    session_token = request.cookies.get("access_token")
    if session_token:
        sub = _sub_desde_jwt(session_token)
        if sub:
            return f"user:{sub}"

    return f"ip:{get_client_ip(request)}"


limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=["10/minute"],
    # Agrega X-RateLimit-* a las respuestas y Retry-After a los 429. Las rutas con
    # @limiter.limit deben recibir `response: Response` para poder inyectarlos.
    headers_enabled=True,
)


# Intentos fallidos de login por email, sin importar la IP de origen (fuerza bruta distribuida).
# Solo cuentan los fallos, y un login correcto reinicia el contador.
LOGIN_FALLIDOS_LIMITE = parse("10 per 15 minutes")


def _email_normalizado(email: str) -> str:
    return email.strip().lower()


def login_bloqueado(email: str) -> bool:
    return not limiter.limiter.test(LOGIN_FALLIDOS_LIMITE, "login_fallido", _email_normalizado(email))


def registrar_login_fallido(email: str) -> None:
    limiter.limiter.hit(LOGIN_FALLIDOS_LIMITE, "login_fallido", _email_normalizado(email))


def reiniciar_login_fallido(email: str) -> None:
    limiter.limiter.clear(LOGIN_FALLIDOS_LIMITE, "login_fallido", _email_normalizado(email))

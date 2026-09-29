import ipaddress
import logging
import time
from contextvars import ContextVar
from datetime import datetime, timezone
from threading import Lock

from jose import JWTError, jwt
from limits import parse
from slowapi import Limiter
from sqlalchemy import or_
from starlette.requests import Request

from app.core.config import ALGORITHM, REDIS_KEY_PREFIX, REDIS_URL, SECRET_KEY
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


def _ip_para_limite(ip: str) -> str:
    """IP normalizada para la clave del rate limit.

    Las IPv6 se agrupan por su /64: los proveedores entregan un bloque completo por
    cliente y, contando por dirección, bastaría rotar dentro del bloque para evadir
    el límite. Los ':' se reemplazan por '-' porque en Redis son separador de
    niveles y cada bloque de la IPv6 aparecía como una carpeta en RedisInsight.
    """
    try:
        direccion = ipaddress.ip_address(ip)
    except ValueError:
        return ip.replace(":", "-")
    if direccion.version == 6 and direccion.ipv4_mapped:
        return str(direccion.ipv4_mapped)
    if direccion.version == 6:
        red = ipaddress.ip_network(f"{direccion}/64", strict=False)
        return str(red).replace(":", "-").replace("/", "_")
    return str(direccion)


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
    # Ya calculada por identificar_cliente; evita decodificar el JWT dos veces
    identidad = getattr(request.state, "rate_limit_key", None)
    if identidad:
        return identidad
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

    return f"ip:{_ip_para_limite(get_client_ip(request))}"


# Límite por defecto según la identidad: las peticiones anónimas cuentan por IP y se
# frenan más; los usuarios y API keys verificados necesitan margen para integraciones
# que consultan en lote (p. ej. estado de guías desde Apps Script o PHP).
LIMITE_ANONIMO = "10/minute"
LIMITE_AUTENTICADO = "120/minute"

_identidad_actual: ContextVar[str] = ContextVar("rate_limit_identidad", default="")


async def identificar_cliente(request: Request, call_next):
    """Middleware que calcula la identidad antes de SlowAPIMiddleware.

    slowapi 0.1.9 no le pasa el request a los límites por defecto dinámicos, así que
    _limite_por_defecto la lee de este ContextVar. Debe registrarse después de
    SlowAPIMiddleware para quedar por fuera de él.
    """
    identidad = get_rate_limit_key(request)
    request.state.rate_limit_key = identidad
    token = _identidad_actual.set(identidad)
    try:
        return await call_next(request)
    finally:
        _identidad_actual.reset(token)


def _limite_por_defecto() -> str:
    # Sin identidad (middleware no registrado) se aplica el límite más estricto
    if _identidad_actual.get().startswith(("user:", "apikey:")):
        return LIMITE_AUTENTICADO
    return LIMITE_ANONIMO


def _storage_config() -> tuple[str, dict]:
    if not REDIS_URL:
        return "memory://", {}
    return REDIS_URL, {
        # Quedan como "<prefijo>:ratelimit:LIMITS/...", aisladas de otros proyectos y entornos
        "key_prefix": f"{REDIS_KEY_PREFIX}:ratelimit",
        # Si Redis no responde rápido se pasa al respaldo en memoria en vez de colgar la petición
        "socket_connect_timeout": 1,
        "socket_timeout": 1,
        "health_check_interval": 30,
    }


_storage_uri, _storage_options = _storage_config()

limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=[_limite_por_defecto],
    # Cuenta por función de la ruta y no por URL: con "url" cada ID (/descargar/1, /descargar/2...)
    # abría un contador propio y el límite no frenaba recorridos por ID.
    key_style="endpoint",
    storage_uri=_storage_uri,
    storage_options=_storage_options,
    # Si Redis cae, slowapi cuenta en memoria del proceso con este límite (ignora los
    # límites propios de cada ruta) y reintenta Redis periódicamente hasta que vuelva.
    in_memory_fallback_enabled=bool(REDIS_URL),
    in_memory_fallback=[_limite_por_defecto] if REDIS_URL else [],
    # Agrega X-RateLimit-* a las respuestas y Retry-After a los 429. Las rutas con
    # @limiter.limit deben recibir `response: Response` para poder inyectarlos.
    headers_enabled=True,
)


# Intentos fallidos de login por email, sin importar la IP de origen (fuerza bruta distribuida).
# Solo cuentan los fallos, y un login correcto reinicia el contador.
LOGIN_FALLIDOS_LIMITE = parse("10 per 15 minutes")


def _email_normalizado(email: str) -> str:
    return email.strip().lower()


# Si el almacenamiento falla (p. ej. Redis caído) no se bloquea el login: el límite
# por IP de la ruta sigue activo vía el respaldo en memoria de slowapi.
def login_bloqueado(email: str) -> bool:
    try:
        return not limiter.limiter.test(LOGIN_FALLIDOS_LIMITE, "login_fallido", _email_normalizado(email))
    except Exception:
        logger.warning("No se pudo consultar el contador de logins fallidos", exc_info=True)
        return False


def registrar_login_fallido(email: str) -> None:
    try:
        limiter.limiter.hit(LOGIN_FALLIDOS_LIMITE, "login_fallido", _email_normalizado(email))
    except Exception:
        logger.warning("No se pudo registrar el login fallido", exc_info=True)


def reiniciar_login_fallido(email: str) -> None:
    try:
        limiter.limiter.clear(LOGIN_FALLIDOS_LIMITE, "login_fallido", _email_normalizado(email))
    except Exception:
        logger.warning("No se pudo reiniciar el contador de logins fallidos", exc_info=True)

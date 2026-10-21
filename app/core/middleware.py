import logging
import re
import uuid

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import DEBUG

logger = logging.getLogger("api")

_STATUS_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMIT_EXCEEDED",
    500: "INTERNAL_ERROR",
}


# Un X-Request-ID enviado por el cliente se reutiliza solo si tiene forma segura
_REQUEST_ID_VALIDO = re.compile(r"^[A-Za-z0-9-]{1,64}$")


def _get_request_id(request: Request) -> str:
    """Id de la petición: el que fijó ErrorHandlingMiddleware o, si no pasó por él, uno nuevo."""
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        return request_id
    entrante = request.headers.get("X-Request-ID", "")
    request_id = entrante if _REQUEST_ID_VALIDO.match(entrante) else str(uuid.uuid4())
    request.state.request_id = request_id
    return request_id


def _error_response(status_code: int, detail, request_id: str, headers: dict | None = None) -> JSONResponse:
    code = _STATUS_CODES.get(status_code, "ERROR")

    if isinstance(detail, dict):
        message = detail.pop("message", str(detail))
        extra = detail  # campos adicionales como is_verified
    else:
        message = str(detail) if detail else "Error desconocido"
        extra = {}

    error = {"code": code, "message": message, **extra}
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": error, "request_id": request_id},
        headers={**(headers or {}), "X-Request-ID": request_id},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """HTTPException de las rutas y también los 404/405 que genera el propio enrutador."""
    request_id = _get_request_id(request)
    logger.warning(
        f"HTTP {exc.status_code} | {request.method} {request.url} | {exc.detail} | request_id={request_id}"
    )
    return _error_response(exc.status_code, exc.detail, request_id, getattr(exc, "headers", None))


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """422 con la lista de campos inválidos. No se devuelve el valor recibido para no exponer datos sensibles."""
    request_id = _get_request_id(request)
    errores = []
    for err in exc.errors():
        loc = [str(parte) for parte in err.get("loc", ())]
        # En JSON mal formado el loc trae la posición del error, no un campo
        campo = None if err.get("type") == "json_invalid" else (".".join(loc[1:]) or None)
        errores.append({
            "ubicacion": loc[0] if loc else None,
            "campo": campo,
            "tipo": err.get("type"),
            "mensaje": err.get("msg"),
        })
    campos = ", ".join(e["campo"] or e["ubicacion"] or "?" for e in errores)
    logger.warning(
        f"HTTP 422 | {request.method} {request.url} | campos inválidos: {campos} | request_id={request_id}"
    )
    detail = {"message": "La petición tiene campos inválidos", "errores": errores}
    return _error_response(422, detail, request_id)


async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """429 con el formato estándar, conservando Retry-After y X-RateLimit-* de slowapi."""
    request_id = _get_request_id(request)
    logger.warning(
        f"HTTP 429 | {request.method} {request.url} | {exc.detail} | request_id={request_id}"
    )
    response = _error_response(429, f"Límite de peticiones excedido: {exc.detail}", request_id)
    view_rate_limit = getattr(request.state, "view_rate_limit", None)
    if view_rate_limit is not None:
        response = request.app.state.limiter._inject_headers(response, view_rate_limit)
    return response


class ErrorHandlingMiddleware:
    async def __call__(self, request: Request, call_next):
        request_id = _get_request_id(request)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            logger.exception(
                f"Unhandled error | {request.method} {request.url} | request_id={request_id}"
            )
            detail = {"message": "Error interno del servidor"}
            if DEBUG:
                detail["detail"] = str(exc)
            return _error_response(500, detail, request_id)
import uuid
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import DEBUG

logger = logging.getLogger("api")

_STATUS_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMIT_EXCEEDED",
    500: "INTERNAL_ERROR",
}


def _error_response(status_code: int, detail, request_id: str) -> JSONResponse:
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
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    logger.warning(
        f"HTTP {exc.status_code} | {request.method} {request.url} | {exc.detail} | request_id={request_id}"
    )
    return _error_response(exc.status_code, exc.detail, request_id)


class ErrorHandlingMiddleware:
    async def __call__(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
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
import uuid
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("api")


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

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "Error interno del servidor"
                    },
                    "request_id": request_id
                }
            )
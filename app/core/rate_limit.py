from slowapi import Limiter
from starlette.requests import Request


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host


limiter = Limiter(
    key_func=get_client_ip,
    default_limits=["10/minute"]
)
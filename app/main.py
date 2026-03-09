from fastapi import FastAPI

# Importar modulos para rateli limit
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.rate_limit import limiter

# Importar modulos para CORS
from fastapi.middleware.cors import CORSMiddleware

# Importar modulos para control errores
from app.core.logging import setup_logging
from app.core.middleware import ErrorHandlingMiddleware

from app.modules.rhu.models import *
from app.modules.tte.models import *

from app.modules.rhu.router import router as rhu_router
from app.modules.tte.router import router as tte_router
from app.modules.gen.router import router as gen_router
from app.modules.auth.router import router as auth_router

setup_logging()

app = FastAPI(title="ERP API")

app.middleware("http")(ErrorHandlingMiddleware())

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


origins = [
    "http://localhost:4200",
    "https://semanticaapi.com.co",
    "http://empleado.co",
    "https://empleado.co",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-API-Key"
    ],
)

app.include_router(rhu_router)
app.include_router(tte_router)
app.include_router(gen_router)
app.include_router(auth_router)

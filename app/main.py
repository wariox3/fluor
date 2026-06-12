from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.observability import setup_sentry

# Importar modulos para rate limit
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.rate_limit import limiter

# Importar modulos para CORS
from fastapi.middleware.cors import CORSMiddleware

# Importar modulos para control errores
from app.core.logging import setup_logging
from app.core.middleware import ErrorHandlingMiddleware, http_exception_handler

from app.core.master_database import Base as MasterBase, engine as master_engine
from app.modules.auth.models import *  # noqa: F401,F403 — registra modelos en MasterBase

from app.modules.rhu.models import *
from app.modules.tte.models import *
from app.modules.tur.models import *
from app.modules.gen.models import *
from app.modules.car.models import *

from app.modules.rhu.router import router as rhu_router
from app.modules.tte.router import router as tte_router
from app.modules.gen.router import router as gen_router
from app.modules.fin.router import router as fin_router
from app.modules.doc.router import router as doc_router
from app.modules.tur.router import router as tur_router
from app.modules.crm.router import router as crm_router
from app.modules.car.router import router as car_router
from app.modules.auth.router import router as auth_router
from app.modules.mas.router import router as mas_router

setup_logging()
# Inicializar Sentry tras el logging y antes de crear la app
setup_sentry()

@asynccontextmanager
async def lifespan(app: FastAPI):    
    MasterBase.metadata.create_all(bind=master_engine)
    yield


app = FastAPI(title="Semantica ERP API", lifespan=lifespan)

app.middleware("http")(ErrorHandlingMiddleware())

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_middleware(SlowAPIMiddleware)


origins = [
    "http://localhost:4200",
    "https://semanticaapi.com.co",
    "https://www.semanticaapi.com.co",
    "https://api.semanticaapi.com.co",
    "https://www.api.semanticaapi.com.co",
    "https://empleado.co",
    "https://www.empleado.co",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-API-Key"]
)

app.include_router(rhu_router)
app.include_router(tte_router)
app.include_router(gen_router)
app.include_router(fin_router)
app.include_router(doc_router)
app.include_router(tur_router)
app.include_router(crm_router)
app.include_router(car_router)
app.include_router(auth_router)
app.include_router(mas_router)


@app.get("/health", include_in_schema=False)
def health():
    """Healthcheck para monitores externos (uptime) y balanceadores.

    Devuelve 200 si la app responde y la Master DB acepta conexiones;
    503 si la base de datos no responde.
    """
    try:
        with master_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "unreachable"},
        )
    return {"status": "ok", "database": "ok"}


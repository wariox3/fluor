from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.rhu.models import *
from app.modules.tte.models import *

from app.modules.rhu.router import router as rhu_router
from app.modules.tte.router import router as tte_router
from app.modules.auth.router import router as auth_router

app = FastAPI(title="ERP API")

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
app.include_router(auth_router)


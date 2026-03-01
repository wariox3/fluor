from fastapi import FastAPI
from app.core.database import engine, Base


from app.modules.rhu.models import *
from app.modules.tte.models import *


from app.modules.rhu.router import router as rhu_router
from app.modules.tte.router import router as tte_router

app = FastAPI(title="ERP API")

Base.metadata.create_all(bind=engine)

app.include_router(rhu_router)
app.include_router(tte_router)
#app.include_router(fin_router)
#app.include_router(tur_router)




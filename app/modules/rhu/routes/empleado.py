from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.tenant_database import get_tenant_db
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.schemas.empleado import EmpleadoResponse

router = APIRouter()

@router.get("/", response_model=List[EmpleadoResponse])
def lista(db: Session = Depends(get_tenant_db)):
    return db.query(Empleado).all()
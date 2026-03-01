from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.schemas.empleado import EmpleadoResponse

router = APIRouter()

@router.get("/", response_model=List[EmpleadoResponse])
def listar_empleados(db: Session = Depends(get_db)):
    return db.query(Empleado).all()


@router.get("/{empleado_id}", response_model=EmpleadoResponse)
def obtener_empleado(empleado_id: int, db: Session = Depends(get_db)):
    empleado = db.query(Empleado).filter(
        Empleado.id == empleado_id
    ).first()

    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    return empleado
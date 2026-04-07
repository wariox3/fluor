from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.models.empleado_actualizacion import EmpleadoActualizacion
from app.modules.rhu.schemas.empleado_actualizacion import EmpleadoActualizacionCreate, EmpleadoActualizacionResponse

router = APIRouter()


@router.post("/nuevo", response_model=EmpleadoActualizacionResponse)
def nuevo(
    data: EmpleadoActualizacionCreate,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    empleado = db.query(Empleado).filter(Empleado.codigo_empleado_pk == data.codigo_empleado_fk).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    actualizacion = EmpleadoActualizacion(
        codigo_empleado_fk=data.codigo_empleado_fk,
        codigo_ciudad_fk=data.codigo_ciudad_fk,
        celular=data.celular,
        telefono=data.telefono,
        direccion=data.direccion,
        barrio=data.barrio,
        fecha=date.today(),
        estado_aplicado=False,
    )
    db.add(actualizacion)
    db.commit()
    db.refresh(actualizacion)
    return actualizacion

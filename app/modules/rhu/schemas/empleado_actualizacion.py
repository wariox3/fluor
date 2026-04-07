from pydantic import BaseModel
from typing import Optional
from datetime import date


class EmpleadoActualizacionCreate(BaseModel):
    codigo_empleado_fk: int
    codigo_ciudad_fk: int
    celular: str
    telefono: str
    direccion: str
    barrio: str


class EmpleadoActualizacionResponse(BaseModel):
    codigo_empleado_actualizacion_pk: int
    codigo_empleado_fk: int
    codigo_ciudad_fk: Optional[int] = None
    celular: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    barrio: Optional[str] = None
    correo: Optional[str] = None
    fecha: Optional[date] = None
    estado_aplicado: Optional[bool] = None

    model_config = {"from_attributes": True}

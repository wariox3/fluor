from pydantic import BaseModel
from typing import Optional

class EmpleadoBase(BaseModel):
    nombre_corto: str
    correo: str  
    correo: Optional[str]  

class EmpleadoResponse(EmpleadoBase):
    codigo_empleado_pk: int

    class Config:
        from_attributes = True
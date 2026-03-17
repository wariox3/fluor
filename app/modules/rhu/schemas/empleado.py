from pydantic import BaseModel
from typing import List, Optional

class EmpleadoBase(BaseModel):
    nombre_corto: str  
    correo: Optional[str]  

class EmpleadoResponse(EmpleadoBase):
    codigo_empleado_pk: int

    class Config:
        from_attributes = True

class EmpleadoResponse(BaseModel):
    codigo_empleado_pk: int
    nombre_corto: str
    numero_identificacion: str
    correo: Optional[str]

    model_config = {"from_attributes": True}


class EmpleadoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[EmpleadoResponse]       
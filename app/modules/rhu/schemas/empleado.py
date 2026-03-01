from pydantic import BaseModel

class EmpleadoBase(BaseModel):
    nombre_corto: str
    correo: str    

class EmpleadoResponse(EmpleadoBase):
    codigo_empleado_pk: int

    class Config:
        from_attributes = True
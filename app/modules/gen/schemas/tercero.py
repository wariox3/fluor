from pydantic import BaseModel
from typing import List, Optional


class TerceroResponse(BaseModel):
    codigo_tercero_pk: int
    nombre_corto: Optional[str] = None
    numero_identificacion: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    critico: Optional[bool] = None
    cliente: Optional[bool] = None
    proveedor: Optional[bool] = None
    empleado: Optional[bool] = None
    prospecto: Optional[bool] = None
    permanente: Optional[bool] = None
    estado_inactivo: Optional[bool] = None
    ciudad_nombre: Optional[str] = None
    codigo_asesor_fk: Optional[int] = None
    asesor_nombre: Optional[str] = None

    model_config = {"from_attributes": True}


class TerceroListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[TerceroResponse]
       
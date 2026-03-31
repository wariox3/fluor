from pydantic import BaseModel
from typing import List, Optional


class SucursalResponse(BaseModel):
    codigo_sucursal_pk: int
    codigo_tercero_fk: Optional[int] = None
    nombre: Optional[str] = None
    correo_factura_electronica: Optional[str] = None
    telefono: Optional[str] = None
    contacto: Optional[str] = None
    direccion: Optional[str] = None
    codigo_ciudad_fk: Optional[int] = None
    codigo_empresa_fk: int
    ciudad_nombre: Optional[str] = None
    tercero_nombre_corto: Optional[str] = None
    tercero_numero_identificacion: Optional[str] = None

    model_config = {"from_attributes": True}


class SucursalListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[SucursalResponse]

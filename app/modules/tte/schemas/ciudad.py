from typing import Optional

from pydantic import BaseModel


class CiudadResponse(BaseModel):
    codigo_ciudad_pk: str
    nombre: Optional[str]
    codigo_departamento_fk: Optional[str]
    departamento_nombre: Optional[str] = None
    codigo_interface: Optional[str]
    codigo_general: Optional[str]
    estado_inactivo: Optional[bool]
    codigo_ruta_fk: Optional[str] = None
    ruta_nombre: Optional[str] = None

    model_config = {"from_attributes": True}


class CiudadListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[CiudadResponse]


class CiudadDescargarResponse(BaseModel):
    codigo_ciudad_pk: str
    nombre: Optional[str]
    departamento_nombre: Optional[str] = None
    codigo_ruta_fk: Optional[str] = None
    orden_ruta: Optional[int] = None
    codigo_zona_fk: Optional[str] = None
    reexpedicion: Optional[bool] = None

    model_config = {"from_attributes": True}


class CiudadSincronizarResponse(BaseModel):
    codigo_ciudad_pk: str
    nombre: Optional[str]
    codigo_division: Optional[str]
    nombre_division: Optional[str]
    codigo_zona: Optional[str]
    nombre_zona: Optional[str]
    codigo_municipio: Optional[str]
    nombre_municipio: Optional[str]
    codigo_departamento_fk: Optional[str]
    codigo_ruta_fk: Optional[str]
    codigo_zona_fk: Optional[str]
    codigo_cuenta_industria_comercio_fk: Optional[str]
    codigo_centro_costo_fk: Optional[str]
    codigo_empresa_fk: int
    orden_ruta: Optional[int]
    codigo_interface: Optional[str]
    codigo_general: Optional[str]
    codigo_universal: Optional[int]
    porcentaje_industria_comercio: float
    vr_base_industria_comercio: float
    lunes: Optional[bool]
    martes: Optional[bool]
    miercoles: Optional[bool]
    jueves: Optional[bool]
    viernes: Optional[bool]
    sabado: Optional[bool]
    domingo: Optional[bool]
    reexpedicion: Optional[bool]
    estado_inactivo: Optional[bool]
    ruteo: bool
    decodificar: bool
    latitud: Optional[str]
    longitud: Optional[str]

    model_config = {"from_attributes": True}

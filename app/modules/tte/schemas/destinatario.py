from typing import Optional

from pydantic import BaseModel, Field


class DestinatarioCreateRequest(BaseModel):
    codigo_identificacion_fk: str = Field(..., min_length=1, max_length=3)
    numero_identificacion: str = Field(..., min_length=1, max_length=20)
    codigo_ciudad_fk: Optional[str] = Field(None, max_length=20)
    codigo_tercero_fk: Optional[int] = None
    digito_verificacion: Optional[str] = Field(None, max_length=1)
    nombre_corto: Optional[str] = Field(None, max_length=150)
    nombre1: Optional[str] = Field(None, max_length=50)
    nombre2: Optional[str] = Field(None, max_length=50)
    apellido1: Optional[str] = Field(None, max_length=50)
    apellido2: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = Field(None, max_length=200)
    telefono: Optional[str] = Field(None, max_length=30)
    movil: Optional[str] = Field(None, max_length=30)
    correo: Optional[str] = Field(None, max_length=1000)
    comentario: Optional[str] = Field(None, max_length=2000)
    estado_inactivo: bool = False


class DestinatarioResponse(BaseModel):
    codigo_destinatario_pk: int
    codigo_identificacion_fk: Optional[str] = None
    identificacion_nombre: Optional[str] = None
    numero_identificacion: Optional[str] = None
    digito_verificacion: Optional[str] = None
    nombre_corto: Optional[str] = None
    nombre1: Optional[str] = None
    nombre2: Optional[str] = None
    apellido1: Optional[str] = None
    apellido2: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    movil: Optional[str] = None
    correo: Optional[str] = None
    codigo_ciudad_fk: Optional[str] = None
    ciudad_nombre: Optional[str] = None
    codigo_tercero_fk: Optional[int] = None
    tercero_nombre: Optional[str] = None
    comentario: Optional[str] = None
    estado_inactivo: Optional[bool] = None

    model_config = {"from_attributes": True}


class DestinatarioListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[DestinatarioResponse]

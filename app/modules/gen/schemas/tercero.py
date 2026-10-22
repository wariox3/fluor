from pydantic import BaseModel, Field
from typing import Optional


class TerceroCreateRequest(BaseModel):
    codigo_identificacion_fk: str = Field(..., max_length=3)
    numero_identificacion: str = Field(..., min_length=1, max_length=20)
    digito_verificacion: Optional[str] = Field(None, max_length=1)
    codigo_ciudad_fk: int
    nombre_corto: Optional[str] = Field(None, max_length=150)
    nombre_extendido: Optional[str] = Field(None, max_length=500)
    codigo_tipo_persona_fk: Optional[str] = Field(None, max_length=3)
    codigo_regimen_fk: Optional[str] = Field(None, max_length=10)
    codigo_postal: Optional[str] = Field(None, max_length=20)
    nombre1: Optional[str] = Field(None, max_length=50)
    nombre2: Optional[str] = Field(None, max_length=50)
    apellido1: Optional[str] = Field(None, max_length=50)
    apellido2: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = Field(None, max_length=200)
    barrio: Optional[str] = Field(None, max_length=80)
    telefono: Optional[str] = Field(None, max_length=30)
    celular: Optional[str] = Field(None, max_length=30)
    correo: Optional[str] = Field(None, max_length=1000)
    codigo_asesor_fk: Optional[int] = None
    codigo_condicion_fk: Optional[int] = None
    codigo_operacion_fk: Optional[str] = Field(None, max_length=20)
    codigo_forma_pago_fk: Optional[str] = Field(None, max_length=10)
    cliente: bool = False
    proveedor: bool = False
    empleado: bool = False
    prospecto: bool = False
    permanente: bool = False
    critico: bool = False
    guia_pago_credito: bool = False
    guia_pago_contado: bool = False
    guia_pago_destino: bool = False
    guia_pago_cortesia: bool = False
    guia_pago_recogida: bool = False
    comentario: Optional[str] = Field(None, max_length=2000)


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
    codigo_condicion_fk: Optional[int] = None
    condicion_nombre: Optional[str] = None
    condicion_codigo_precio_fk: Optional[int] = None
    codigo_operacion_fk: Optional[str] = None

    model_config = {"from_attributes": True}


class TerceroDetalleResponse(TerceroResponse):
    codigo_identificacion_fk: Optional[str] = None
    digito_verificacion: Optional[str] = None
    nombre_extendido: Optional[str] = None
    codigo_tipo_persona_fk: Optional[str] = None
    tipo_persona_nombre: Optional[str] = None
    codigo_regimen_fk: Optional[str] = None
    regimen_nombre: Optional[str] = None
    codigo_postal: Optional[str] = None
    codigo_ciudad_fk: Optional[int] = None
    nombre1: Optional[str] = None
    nombre2: Optional[str] = None
    apellido1: Optional[str] = None
    apellido2: Optional[str] = None
    celular: Optional[str] = None
    barrio: Optional[str] = None
    codigo_forma_pago_fk: Optional[str] = None
    comentario: Optional[str] = None
    guia_pago_credito: Optional[bool] = None
    guia_pago_contado: Optional[bool] = None
    guia_pago_destino: Optional[bool] = None
    guia_pago_cortesia: Optional[bool] = None
    guia_pago_recogida: Optional[bool] = None


class TerceroListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[TerceroResponse]
       

class TerceroBuscarResponse(BaseModel):
    codigo_tercero_pk: int
    numero_identificacion: Optional[str] = None
    nombre_corto: Optional[str] = None
    condicion_nombre: Optional[str] = None
    estado_inactivo: Optional[bool] = None

    model_config = {"from_attributes": True}


class TerceroBuscarListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[TerceroBuscarResponse]

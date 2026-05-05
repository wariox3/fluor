from datetime import datetime
from typing import List, Optional, Annotated

from pydantic import BaseModel, Field

class GuiaBase(BaseModel):
    documento_cliente: str

class GuiaCreateRequest(BaseModel):
    codigo_guia_tipo_fk: str
    codigo_operacion_ingreso_fk: str
    codigo_tercero_fk: int
    codigo_adquiriente_fk: int
    codigo_empaque_fk: str
    codigo_producto_fk: str
    codigo_servicio_fk: str
    codigo_ciudad_origen_fk: str
    codigo_ciudad_destino_fk: str
    documento_cliente: Optional[str] = None
    remitente: str
    nombre_destinatario: str
    direccion_destinatario: str
    telefono_destinatario: str
    unidades: float
    peso_real: float
    peso_volumen: float
    peso_facturado: float
    vr_flete: float
    vr_manejo: float
    vr_declara: float
    estado_recogido: bool
    estado_ingreso: bool

class GuiaCreateResponse(BaseModel):
    codigo_guia_pk: int
    codigo_guia_tipo_fk: str
    codigo_operacion_ingreso_fk: str
    codigo_tercero_fk: int
    codigo_adquiriente_fk: int
    codigo_empaque_fk: str
    codigo_producto_fk: str
    codigo_servicio_fk: str
    codigo_ciudad_origen_fk: str
    codigo_ciudad_destino_fk: str
    documento_cliente: Optional[str] = None
    remitente: str
    nombre_destinatario: str
    direccion_destinatario: str
    telefono_destinatario: str
    unidades: float
    peso_real: float
    peso_volumen: float
    peso_facturado: float
    vr_flete: float
    vr_manejo: float
    vr_declara: float
    estado_recogido: bool
    estado_ingreso: bool

    class Config:
        from_attributes = True

class GuiaCorreccionRequest(BaseModel):
    unidades: float
    peso_real: float
    peso_volumen: float
    peso_facturado: float


class GuiaCorreccionResponse(BaseModel):
    codigo_guia_pk: int
    unidades: float
    peso_real: float
    peso_volumen: float
    peso_facturado: float
    correccion: bool

    model_config = {"from_attributes": True}


class GuiasMasivoRequest(BaseModel):
    guias: Annotated[List[int], Field(min_length=1, max_length=1000)]


class GuiaResponse(BaseModel):
    codigo_guia_pk: int
    codigo_guia_tipo_fk: Optional[str]
    codigo_tercero_fk: Optional[int]
    codigo_adquiriente_fk: Optional[int]
    codigo_ciudad_origen_fk: Optional[str]
    codigo_ciudad_destino_fk: Optional[str]
    codigo_ruta_fk: Optional[str]
    documento_cliente: Optional[str]
    remitente: Optional[str]
    nombre_destinatario: Optional[str]
    direccion_destinatario: Optional[str]
    telefono_destinatario: Optional[str]
    unidades: Optional[float]
    peso_real: Optional[float]
    peso_volumen: Optional[float]
    peso_facturado: Optional[float]
    vr_flete: Optional[float]
    vr_manejo: Optional[float]
    vr_declara: Optional[float]
    estado_recogido: bool
    fecha_recogido: Optional[datetime]
    estado_ingreso: bool
    fecha_ingreso: Optional[datetime]
    estado_despachado: bool
    fecha_despacho: Optional[datetime]
    estado_entregado: bool
    fecha_entrega: Optional[datetime]
    estado_cumplido: bool
    fecha_cumplido: Optional[datetime]
    estado_novedad: bool
    estado_novedad_solucion: bool

    model_config = {"from_attributes": True}


class GuiaListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[GuiaResponse]


class GuiaEstadoResponse(BaseModel):
    codigo_guia_pk: int
    documento_cliente: Optional[str]
    estado_recogido: bool
    fecha_recogido: Optional[datetime]
    estado_ingreso: bool
    fecha_ingreso: Optional[datetime]
    estado_despachado: bool
    fecha_despacho: Optional[datetime]
    estado_entregado: bool
    fecha_entrega: Optional[datetime]
    estado_cumplido: bool
    fecha_cumplido: Optional[datetime]
    estado_novedad: bool
    estado_novedad_solucion: bool

    model_config = {"from_attributes": True}

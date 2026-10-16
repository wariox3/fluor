from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SeguimientoCreateRequest(BaseModel):
    codigo_guia_fk: int
    codigo_seguimiento_tipo_fk: Optional[str] = None
    codigo_operacion_fk: Optional[str] = None
    fecha_seguimiento: Optional[datetime] = None
    comentario: Optional[str] = None
    datos: Optional[str] = None
    latitud: float = 0.0
    longitud: float = 0.0


class SeguimientoActualizarInterfaceRequest(BaseModel):
    actualizar_guia: bool = False


class SeguimientoResponse(BaseModel):
    codigo_seguimiento_pk: int
    codigo_guia_fk: Optional[int]
    codigo_seguimiento_tipo_fk: Optional[str]
    codigo_operacion_fk: Optional[str]
    fecha: Optional[datetime]
    fecha_seguimiento: Optional[datetime]
    usuario: Optional[str]
    comentario: Optional[str]
    datos: Optional[str]
    estado_interface: bool
    estado_descartado: bool
    latitud: Optional[float]
    longitud: Optional[float]

    model_config = {"from_attributes": True}


class SeguimientoListItemResponse(SeguimientoResponse):
    seguimiento_tipo_nombre: Optional[str] = None
    guia_fecha_ingreso: Optional[datetime] = None
    guia_fecha_ingreso_operacion: Optional[datetime] = None
    guia_documento_cliente: Optional[str] = None
    guia_documento_cliente_tipo: Optional[str] = None
    guia_nombre_destinatario: Optional[str] = None
    guia_telefono_destinatario: Optional[str] = None
    guia_codigo_tercero_operacion_fk: Optional[int] = None
    guia_estado_interface_soporte: Optional[bool] = None
    guia_despacho_fecha_salida: Optional[datetime] = None


class SeguimientoListResponse(BaseModel):
    total: int
    total_exacto: bool
    page: int
    size: int
    items: list[SeguimientoListItemResponse]


class SeguimientoDetalleGuiaResponse(BaseModel):
    codigo_seguimiento_pk: int
    codigo_seguimiento_tipo_fk: Optional[str]
    codigo_guia_fk: Optional[int]
    fecha: Optional[datetime]
    fecha_seguimiento: Optional[datetime]
    usuario: Optional[str]
    codigo_operacion_fk: Optional[str]
    comentario: Optional[str]
    datos: Optional[str]
    guia_documento_cliente: Optional[str]
    guia_fecha_entrega: Optional[datetime]
    seguimiento_tipo_nombre: Optional[str]
    ciudad_destino_codigo_municipio: Optional[str]


class SeguimientoDetalleArchivoResponse(BaseModel):
    base64: Optional[str]

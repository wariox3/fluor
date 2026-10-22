from datetime import datetime
from typing import Optional, Annotated

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
    documento_cliente_tipo: Optional[str] = Field(None, max_length=20)
    codigo_tercero_operacion_fk: Optional[int] = None
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
    vr_recaudo: float = 0.0
    estado_recogido: bool
    estado_ingreso: bool
    devolver_documento_cliente: bool = False
    liquidar: bool = False
    condicion: Optional[int] = None
    precio: Optional[int] = None
    zona: Optional[str] = None
    tipo_liquidacion: str = "K"
    comentario: str
    # Opcionales: si no llegan se usan los valores calculados (ver /tte/guia/nuevo)
    codigo_operacion_cargo_fk: Optional[str] = Field(None, max_length=20)
    relacion_cliente: Optional[str] = Field(None, max_length=100)
    direccion_remitente: Optional[str] = Field(None, max_length=150)
    telefono_remitente: Optional[str] = Field(None, max_length=80)
    codigo_identificacion_destinatario_fk: Optional[str] = Field(None, max_length=3)
    numero_identificacion_destinatario: Optional[str] = Field(None, max_length=20)
    codigo_destinatario_fk: Optional[int] = None
    codigo_ruta_fk: Optional[str] = Field(None, max_length=20)
    orden_ruta: Optional[int] = None
    codigo_asesor_fk: Optional[int] = None
    vr_otros: float = 0.0
    empaque_referencia: Optional[str] = Field(None, max_length=80)
    mercancia_peligrosa: bool = False
    contenido_verificado: bool = False

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
    vr_recaudo: float
    vr_cobro_entrega: float
    tipo_liquidacion: Optional[str] = None
    estado_recogido: bool
    estado_ingreso: bool
    devolver_documento_cliente: bool
    codigo_operacion_cargo_fk: Optional[str] = None
    relacion_cliente: Optional[str] = None
    direccion_remitente: Optional[str] = None
    telefono_remitente: Optional[str] = None
    codigo_identificacion_destinatario_fk: Optional[str] = None
    numero_identificacion_destinatario: Optional[str] = None
    codigo_destinatario_fk: Optional[int] = None
    codigo_ruta_fk: Optional[str] = None
    orden_ruta: Optional[int] = None
    codigo_asesor_fk: Optional[int] = None
    vr_otros: Optional[float] = None
    empaque_referencia: Optional[str] = None
    mercancia_peligrosa: Optional[bool] = None
    contenido_verificado: Optional[bool] = None

    class Config:
        from_attributes = True

class GuiaCorreccionRequest(BaseModel):
    unidades: Optional[float] = Field(default=None, ge=0)
    peso_real: Optional[float] = Field(default=None, ge=0)
    peso_volumen: Optional[float] = Field(default=None, ge=0)
    peso_facturado: Optional[float] = Field(default=None, ge=0)
    vr_declara: Optional[float] = Field(default=None, ge=0)
    vr_flete: Optional[float] = Field(default=None, ge=0)
    vr_manejo: Optional[float] = Field(default=None, ge=0)
    vr_recaudo: Optional[float] = Field(default=None, ge=0)
    cortesia: Optional[bool] = None
    codigo_ciudad_destino_fk: Optional[str] = None


class GuiaCorreccionResponse(BaseModel):
    codigo_guia_pk: int
    codigo_ciudad_destino_fk: Optional[str]
    codigo_ruta_fk: Optional[str]
    unidades: float
    peso_real: float
    peso_volumen: float
    peso_facturado: float
    vr_declara: float
    vr_flete: float
    vr_manejo: float
    vr_recaudo: float
    vr_cobro_entrega: float
    cortesia: bool
    correccion: bool

    model_config = {"from_attributes": True}


class GuiaRecogidoRequest(BaseModel):
    guia: int


class GuiaRecogidoResponse(BaseModel):
    codigo_guia_pk: int
    estado_recogido: bool
    fecha_recogido: Optional[datetime]

    model_config = {"from_attributes": True}


class GuiaIngresoRequest(BaseModel):
    guia: int


class GuiaIngresoResponse(BaseModel):
    codigo_guia_pk: int
    estado_ingreso: bool
    fecha_ingreso_operacion: Optional[datetime]

    model_config = {"from_attributes": True}


class GuiasMasivoRequest(BaseModel):
    guias: Annotated[list[int], Field(min_length=1, max_length=1000)]


class GuiasDocumentoMasivoRequest(BaseModel):
    codigo_tercero: int
    documentos: Annotated[list[str], Field(min_length=1, max_length=1000)]


class LiquidarRequest(BaseModel):
    tercero: int
    condicion: Optional[int] = None
    precio: int
    origen: str
    destino: str
    producto: str
    zona: Optional[str] = None
    tipo_liquidacion: str = "K"
    unidades: float = 0.0
    peso: float = 0.0
    volumen: float = 0.0
    declarado: float = 0.0


class LiquidarResponse(BaseModel):
    error: bool = False
    flete: float
    manejo: float
    peso_facturado: float


class ReliquidarRequest(BaseModel):
    codigo_guia_pk: int
    zona: Optional[str] = None
    tipo_liquidacion: Optional[str] = None


class ReliquidarResponse(BaseModel):
    codigo_guia_pk: int
    tipo_liquidacion: Optional[str]
    peso_facturado: float
    vr_flete: float
    vr_manejo: float
    vr_cobro_entrega: float
    correccion: bool

    model_config = {"from_attributes": True}


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
    items: list[GuiaResponse]


class GuiaEstadoResponse(BaseModel):
    codigo_guia_pk: int
    codigo_guia_tipo_fk: Optional[str]
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
    estado_anulado: bool
    vr_recaudo: float
    vr_cobro_entrega: float

    model_config = {"from_attributes": True}


class GuiaDetalleResponse(BaseModel):
    codigo_guia_pk: int
    codigo_guia_tipo_fk: Optional[str]
    guia_tipo_nombre: Optional[str] = None
    codigo_operacion_ingreso_fk: Optional[str]
    operacion_ingreso_nombre: Optional[str] = None
    codigo_operacion_cargo_fk: Optional[str]
    operacion_cargo_nombre: Optional[str] = None
    codigo_tercero_fk: Optional[int]
    tercero_nombre: Optional[str] = None
    codigo_adquiriente_fk: Optional[int]
    adquiriente_nombre: Optional[str] = None
    codigo_asesor_fk: Optional[int]
    asesor_nombre: Optional[str] = None
    codigo_ciudad_origen_fk: Optional[str]
    ciudad_origen_nombre: Optional[str] = None
    codigo_ciudad_destino_fk: Optional[str]
    ciudad_destino_nombre: Optional[str] = None
    codigo_servicio_fk: Optional[str]
    servicio_nombre: Optional[str] = None
    codigo_producto_fk: Optional[str]
    producto_nombre: Optional[str] = None
    codigo_empaque_fk: Optional[str]
    empaque_nombre: Optional[str] = None
    codigo_tercero_operacion_fk: Optional[int]
    codigo_ruta_fk: Optional[str]
    codigo_zona_fk: Optional[str]
    orden_ruta: Optional[int]
    codigo_despacho_fk: Optional[int]
    codigo_condicion_fk: Optional[int]
    condicion_nombre: Optional[str] = None
    codigo_factura_fk: Optional[int]
    numero_factura: Optional[int]

    documento_cliente: Optional[str]
    documento_cliente_tipo: Optional[str]
    relacion_cliente: Optional[str]

    remitente: Optional[str]
    direccion_remitente: Optional[str]
    telefono_remitente: Optional[str]

    codigo_destinatario_fk: Optional[int]
    codigo_identificacion_destinatario_fk: Optional[str]
    numero_identificacion_destinatario: Optional[str]
    nombre_destinatario: Optional[str]
    direccion_destinatario: Optional[str]
    telefono_destinatario: Optional[str]

    fecha_ingreso: Optional[datetime]
    fecha_recogido: Optional[datetime]
    fecha_ingreso_operacion: Optional[datetime]
    fecha_despacho: Optional[datetime]
    fecha_entrega: Optional[datetime]
    fecha_cumplido: Optional[datetime]
    fecha_soporte: Optional[datetime]
    fecha_factura: Optional[datetime]

    unidades: float
    peso_real: float
    peso_volumen: float
    peso_facturado: float
    vr_declara: float
    vr_flete: float
    vr_manejo: float
    vr_recaudo: float
    vr_abono: float
    vr_cobro_entrega: float
    vr_otros: float
    tipo_liquidacion: Optional[str]
    cantidad_despachos: int

    estado_recogido: bool
    estado_ingreso: bool
    estado_impreso: bool
    estado_embarcado: bool
    estado_despachado: bool
    estado_entregado: bool
    estado_soporte: bool
    estado_cumplido: bool
    estado_facturado: bool
    estado_anulado: bool
    estado_novedad: bool
    estado_novedad_solucion: bool
    estado_devolucion: bool

    factura: bool
    cortesia: bool
    correccion: bool
    reexpedicion: bool
    devolver_documento_cliente: bool
    mercancia_peligrosa: Optional[bool]
    contenido_verificado: Optional[bool]
    empaque_referencia: Optional[str]
    usuario: Optional[str]
    comentario: Optional[str]

    model_config = {"from_attributes": True}


class GuiaFormatoImpresionResponse(BaseModel):
    codigo: int
    nombre: str
    predeterminado: bool

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from typing import Literal, Optional
from app.modules.gen.schemas.movimiento_detalle import MovimientoDetalleCreate, MovimientoDetalleResponse

class MovimientoResponse(BaseModel):
    model_config = {"from_attributes": True}

    codigo_movimiento_pk: int
    codigo_movimiento_tipo_fk: str
    codigo_forma_pago_fk: Optional[str] = None
    codigo_asesor_fk: Optional[int] = None
    codigo_movimiento_clase_fk: str
    codigo_sucursal_fk: Optional[int] = None
    codigo_movimiento_fk: Optional[int] = None
    prefijo: Optional[str] = None
    numero: Optional[int] = None
    direccion: Optional[str] = None
    fecha: Optional[datetime] = None
    fecha_documento: Optional[date] = None
    fecha_vence: Optional[date] = None
    fecha_electronico: Optional[datetime] = None
    fecha_entrega: Optional[datetime] = None
    plazo_pago: Optional[int] = None
    vr_flete: Optional[float] = 0.0
    vr_manejo: Optional[float] = 0.0
    codigo_tercero_fk: Optional[int] = None
    codigo_tercero_destino_fk: Optional[int] = None
    codigo_contacto_fk: Optional[int] = None
    soporte: Optional[str] = None
    orden_compra: Optional[str] = None
    orden_ingreso: Optional[str] = None
    remision: Optional[str] = None
    vr_base_iva: Optional[float] = 0.0
    vr_iva: Optional[float] = 0.0
    vr_base_aiu: Optional[float] = 0.0
    vr_subtotal_bruto: Optional[float] = 0.0
    vr_subtotal: Optional[float] = 0.0
    vr_descuento: Optional[float] = 0.0
    vr_neto: Optional[float] = 0.0
    vr_total: Optional[float] = 0.0
    vr_retencion_fuente: Optional[float] = 0.0
    vr_retencion_iva: Optional[float] = 0.0
    vr_autoretencion: Optional[float] = 0.0
    vr_retencion_industria_comercio: Optional[float] = 0.0
    vr_anticipo: Optional[float] = 0.0
    comentarios: Optional[str] = None
    usuario: Optional[str] = None
    fecha_aprobado: Optional[datetime] = None
    usuario_aprobado: Optional[str] = None
    usuario_externo: Optional[str] = None
    estado_autorizado: Optional[bool] = False
    estado_aprobado: Optional[bool] = False
    estado_anulado: Optional[bool] = False
    estado_contabilizado: Optional[bool] = False
    estado_generado: Optional[bool] = False
    estado_electronico: Optional[bool] = False
    estado_descartado_electronico: Optional[bool] = False
    estado_notificado_electronico: Optional[bool] = False
    respuesta_electronico: Optional[str] = None
    respuesta_electronico_fecha: Optional[datetime] = None
    proceso_factura_electronica: Optional[str] = None
    operacion_inventario: Optional[int] = None
    operacion_comercial: Optional[int] = None
    operacion_control: Optional[int] = None
    codigo_resolucion_fk: Optional[int] = None
    codigo_moneda_fk: Optional[str] = None
    cue: Optional[str] = None
    codigo_externo: Optional[str] = None
    cadena_codigo_qr: Optional[str] = None
    genera_costo_promedio: Optional[bool] = False
    guia: Optional[str] = None
    codigo_centro_costo_fk: Optional[str] = None
    codigo_bodega_fk: Optional[str] = None
    codigo_ubicacion_fk: Optional[str] = None
    codigo_sede_fk: Optional[str] = None
    codigo_temporal_orden_compra: Optional[int] = None
    codigo_movimiento_concepto_fk: Optional[str] = None
    codigo_impuesto_industria_comercio_fk: Optional[str] = None
    vr_base_impuesto_industria_comercio_propuesto: Optional[float] = 0.0
    vr_base_impuesto_industria_comercio: Optional[float] = 0.0
    codigo_empresa_fk: int
    codigo_interface: Optional[str] = None
    detalles: Optional[List[MovimientoDetalleResponse]] = None


class MovimientoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[MovimientoResponse]

class MovimientoCreate(BaseModel):
    codigo_tercero_fk: int
    codigo_centro_costo_fk: str
    codigo_movimiento_tipo_fk: str
    codigo_resolucion_fk: Optional[int] = None
    codigo_forma_pago_fk: Optional[int] = None
    comentarios: Optional[str] = None
    orden_compra: Optional[str] = None
    codigo_interface: Optional[str] = None    
    soporte: Optional[str] = None
    plazo_pago: int
    fecha: datetime
    fecha_vence: date
    detalles: List[MovimientoDetalleCreate] = []
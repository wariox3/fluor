from pydantic import BaseModel, Field
from typing import List, Optional


class ItemResponse(BaseModel):
    codigo_item_pk: int
    nombre: Optional[str] = None
    nombre_tecnico: Optional[str] = None
    vr_costo_predeterminado: Optional[float] = 0.0
    vr_costo_promedio: Optional[float] = 0.0
    vr_precio_predeterminado: Optional[float] = 0.0
    vr_precio_promedio: Optional[float] = 0.0
    codigo_ean: Optional[str] = None
    codigo_barras: Optional[str] = None
    porcentaje_iva: Optional[int] = 0
    codigo_linea_fk: Optional[str] = None
    codigo_grupo_fk: Optional[str] = None
    codigo_turno_item_fk: Optional[int] = None
    codigo_subgrupo_fk: Optional[str] = None
    codigo_unidad_medida_fk: Optional[str] = None
    codigo_marca_fk: Optional[str] = None
    codigo_impuesto_retencion_fk: Optional[str] = None
    codigo_impuesto_retencion_compra_fk: Optional[str] = None
    codigo_impuesto_iva_venta_fk: Optional[str] = None
    codigo_impuesto_iva_compra_fk: Optional[str] = None
    codigo_impuesto_industria_comercio_fk: Optional[str] = None
    codigo_medida_fk: Optional[str] = None
    modelo: Optional[str] = None
    referencia: Optional[str] = None
    cantidad_existencia: Optional[int] = 0
    cantidad_remisionada: Optional[int] = 0
    cantidad_control: Optional[int] = 0
    cantidad_reservada: Optional[int] = 0
    cantidad_disponible: Optional[int] = 0
    cantidad_orden: Optional[int] = 0
    cantidad_solicitud_compra: Optional[int] = 0
    cantidad_solicitud: Optional[int] = 0
    cantidad_pedido: Optional[int] = 0
    afecta_inventario: Optional[bool] = True
    retencion_industria_comercio: Optional[bool] = False
    descripcion: Optional[str] = None
    stock_minimo: Optional[int] = 0
    stock_maximo: Optional[int] = 0
    codigo_cuenta_venta_fk: Optional[str] = None
    codigo_cuenta_venta_devolucion_fk: Optional[str] = None
    codigo_cuenta_compra_fk: Optional[str] = None
    codigo_cuenta_compra_devolucion_fk: Optional[str] = None
    codigo_cuenta_compra_importacion_fk: Optional[str] = None
    codigo_cuenta_costo_fk: Optional[str] = None
    codigo_cuenta_inventario_fk: Optional[str] = None
    codigo_cuenta_inventario_transito_fk: Optional[str] = None
    producto: Optional[bool] = False
    servicio: Optional[bool] = False
    servicio_aiu: Optional[bool] = False
    validar_stock: Optional[bool] = False
    activo_fijo: Optional[bool] = False
    registro_invima: Optional[str] = None
    dotacion: Optional[bool] = False
    maneja_serie: Optional[bool] = False
    aplica_turno: Optional[bool] = False
    venta: Optional[bool] = False
    compra: Optional[bool] = True
    talla: Optional[str] = None
    codigo_dotacion_elemento_fk: Optional[int] = None
    estado_inactivo: Optional[bool] = False
    codigo_interface: Optional[str] = None

    model_config = {"from_attributes": True}


class ItemListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ItemResponse]


class ItemCreate(BaseModel):
    nombre: str
    nombre_tecnico: Optional[str] = None
    vr_costo_predeterminado: Optional[float] = 0.0
    vr_costo_promedio: Optional[float] = 0.0
    vr_precio_predeterminado: Optional[float] = 0.0
    vr_precio_promedio: Optional[float] = 0.0
    codigo_ean: Optional[str] = None
    codigo_barras: Optional[str] = None
    porcentaje_iva: Optional[int] = 0
    codigo_linea_fk: Optional[str] = None
    codigo_grupo_fk: Optional[str] = None
    codigo_turno_item_fk: Optional[int] = None
    codigo_subgrupo_fk: Optional[str] = None
    codigo_unidad_medida_fk: Optional[str] = None
    codigo_marca_fk: Optional[str] = None
    codigo_impuesto_retencion_fk: str
    codigo_impuesto_retencion_compra_fk: str
    codigo_impuesto_iva_venta_fk: str
    codigo_impuesto_iva_compra_fk: str
    codigo_impuesto_industria_comercio_fk: Optional[str] = None
    codigo_medida_fk: Optional[str] = None
    modelo: Optional[str] = None
    referencia: Optional[str] = None
    afecta_inventario: bool
    retencion_industria_comercio: Optional[bool] = False
    descripcion: Optional[str] = None
    stock_minimo: Optional[int] = 0
    stock_maximo: Optional[int] = 0
    codigo_cuenta_venta_fk: Optional[str] = None
    codigo_cuenta_venta_devolucion_fk: Optional[str] = None
    codigo_cuenta_compra_fk: Optional[str] = None
    codigo_cuenta_compra_devolucion_fk: Optional[str] = None
    codigo_cuenta_compra_importacion_fk: Optional[str] = None
    codigo_cuenta_costo_fk: Optional[str] = None
    codigo_cuenta_inventario_fk: Optional[str] = None
    codigo_cuenta_inventario_transito_fk: Optional[str] = None
    producto: bool
    servicio: Optional[bool] = False
    servicio_aiu: Optional[bool] = False
    validar_stock: Optional[bool] = False
    activo_fijo: Optional[bool] = False
    registro_invima: Optional[str] = None
    dotacion: Optional[bool] = False
    maneja_serie: Optional[bool] = False
    aplica_turno: Optional[bool] = False
    venta: bool
    compra: bool
    talla: Optional[str] = None
    codigo_dotacion_elemento_fk: Optional[int] = None
    estado_inactivo: Optional[bool] = False
    codigo_interface: Optional[str] = Field(None, max_length=20)


class ItemUpdate(ItemCreate):
    pass

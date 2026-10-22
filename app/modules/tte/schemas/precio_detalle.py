from typing import Optional

from pydantic import BaseModel


class PrecioDetalleResponse(BaseModel):
    codigo_precio_detalle_pk: int
    codigo_precio_fk: Optional[int] = None
    codigo_ciudad_origen_fk: Optional[str] = None
    ciudad_origen_nombre: Optional[str] = None
    codigo_ciudad_destino_fk: Optional[str] = None
    ciudad_destino_nombre: Optional[str] = None
    codigo_zona_fk: Optional[str] = None
    zona_nombre: Optional[str] = None
    codigo_producto_fk: Optional[str] = None
    producto_nombre: Optional[str] = None
    codigo_cobertura_fk: Optional[str] = None
    vr_peso: Optional[float] = None
    vr_unidad: Optional[float] = None
    peso_tope: Optional[float] = None
    vr_peso_tope: Optional[float] = None
    vr_peso_tope_adicional: Optional[float] = None
    minimo: Optional[int] = None

    model_config = {"from_attributes": True}


class PrecioDetalleListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[PrecioDetalleResponse]


class PrecioDetalleProductoClienteResponse(BaseModel):
    codigo_producto_pk: str
    nombre: Optional[str] = None

    model_config = {"from_attributes": True}

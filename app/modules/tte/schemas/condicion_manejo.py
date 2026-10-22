from typing import Optional

from pydantic import BaseModel, Field


class CondicionManejoResponse(BaseModel):
    codigo_condicion_manejo_pk: int
    codigo_cliente_fk: Optional[int] = None
    codigo_tercero_fk: Optional[int] = None
    tercero_nombre: Optional[str] = None
    codigo_ciudad_origen_fk: Optional[str] = None
    ciudad_origen_nombre: Optional[str] = None
    codigo_ciudad_destino_fk: Optional[str] = None
    ciudad_destino_nombre: Optional[str] = None
    codigo_zona_fk: Optional[str] = None
    zona_nombre: Optional[str] = None
    codigo_cobertura_fk: Optional[str] = None
    codigo_pago_fk: Optional[str] = None
    porcentaje: Optional[float] = None
    minimo_unidad: Optional[float] = None
    minimo_despacho: Optional[float] = None

    model_config = {"from_attributes": True}


class CondicionManejoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[CondicionManejoResponse]


class CondicionManejoLiquidarRequest(BaseModel):
    codigo_tercero_fk: int
    codigo_ciudad_origen_fk: Optional[str] = Field(None, max_length=20)
    codigo_ciudad_destino_fk: Optional[str] = Field(None, max_length=20)
    codigo_zona_fk: Optional[str] = Field(None, max_length=20)
    codigo_cobertura_fk: Optional[str] = Field(None, max_length=3)
    codigo_pago_fk: Optional[str] = Field(None, max_length=3)


class CondicionManejoLiquidarResponse(BaseModel):
    codigo_condicion_manejo_pk: int
    porcentaje: float
    minimo_unidad: float
    minimo_despacho: float

    model_config = {"from_attributes": True}

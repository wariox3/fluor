from typing import Optional

from pydantic import BaseModel, Field


class CondicionFleteResponse(BaseModel):
    codigo_condicion_flete_pk: int
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
    descuento_peso: Optional[float] = None
    descuento_unidad: Optional[float] = None
    peso_minimo: Optional[int] = None
    peso_minimo_guia: Optional[int] = None
    flete_minimo: Optional[float] = None
    flete_minimo_guia: Optional[float] = None
    vr_peso: Optional[float] = None
    vr_unidad: Optional[float] = None

    model_config = {"from_attributes": True}


class CondicionFleteListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[CondicionFleteResponse]


class CondicionFleteLiquidarRequest(BaseModel):
    codigo_tercero_fk: int
    codigo_ciudad_origen_fk: Optional[str] = Field(None, max_length=20)
    codigo_ciudad_destino_fk: Optional[str] = Field(None, max_length=20)
    codigo_zona_fk: Optional[str] = Field(None, max_length=20)
    codigo_cobertura_fk: Optional[str] = Field(None, max_length=3)
    codigo_pago_fk: Optional[str] = Field(None, max_length=3)


class CondicionFleteLiquidarResponse(BaseModel):
    codigo_condicion_flete_pk: int
    descuento_peso: float
    descuento_unidad: float
    peso_minimo: int
    peso_minimo_guia: int
    flete_minimo: float
    flete_minimo_guia: float

    model_config = {"from_attributes": True}

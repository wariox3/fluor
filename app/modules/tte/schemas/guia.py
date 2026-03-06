from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class GuiaBase(BaseModel):
    documento_cliente: str

class GuiaResponse(GuiaBase):
    codigo_guia_pk: int
    documento_cliente: str
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

class GuiaEstadoResponse(GuiaBase):
    codigo_guia_pk: int
    documento_cliente: str
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

    class Config:
        from_attributes = True
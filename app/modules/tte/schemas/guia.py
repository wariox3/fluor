from datetime import datetime
from typing import List, Optional, Annotated

from pydantic import BaseModel, Field

class GuiaBase(BaseModel):
    documento_cliente: str

class GuiaCreateRequest(BaseModel):
    codigo_guia_pk: int    
    codigo_guia_tipo_fk: str
    codigo_operacion_ingreso_fk: str
    codigo_tercero_fk: int
    unidades: float
    peso_real: float
    peso_volumen: float
    vr_flete: float
    vr_manejo: float
    vr_declara: float

class GuiasMasivoRequest(BaseModel):
    guias: Annotated[List[int], Field(min_length=1, max_length=1000)] 

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

       
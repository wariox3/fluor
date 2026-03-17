from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProgramacionResponse(BaseModel):
    codigo_programacion_pk: int

    model_config = {"from_attributes": True}


class ProgramacionListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ProgramacionResponse]

class ProgramacionItem(BaseModel):
    codigo_programacion_pk: int
    puesto_nombre: Optional[str]
    puesto_direccion: Optional[str]
    coordinador_nombre: Optional[str]
    programador_nombre: Optional[str]
    codigo_modalidad_fk: Optional[str]
    tercero_nombre_corto: Optional[str]
    dia_1: str
    dia_2: str
    dia_3: str
    dia_4: str
    dia_5: str
    dia_6: str
    dia_7: str
    dia_8: str
    dia_9: str
    dia_10: str
    dia_11: str
    dia_12: str
    dia_13: str
    dia_14: str
    dia_15: str
    dia_16: str
    dia_17: str
    dia_18: str
    dia_19: str
    dia_20: str
    dia_21: str
    dia_22: str
    dia_23: str
    dia_24: str
    dia_25: str
    dia_26: str
    dia_27: str
    dia_28: str
    dia_29: str
    dia_30: str
    dia_31: str

       
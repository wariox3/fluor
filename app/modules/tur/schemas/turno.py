from pydantic import BaseModel
from typing import List, Optional
from datetime import time


class TurnoResponse(BaseModel):
    codigo_turno_pk: str
    nombre: Optional[str]
    hora_desde: Optional[time]
    hora_hasta: Optional[time]
    horas: float
    horas_diurnas: float
    horas_nocturnas: float
    horas_recargo_nocturno: float
    novedad: bool
    descanso: bool
    descanso_ordinario: bool
    incapacidad: bool
    incapacidad_no_legalizada: bool
    licencia: bool
    licencia_no_remunerada: bool
    vacacion: bool
    ingreso: bool
    retiro: bool
    induccion: bool
    ausentismo: Optional[bool]
    dia: Optional[bool]
    noche: Optional[bool]
    complementario: bool
    adicional: bool
    completo: bool
    disponible: bool
    vr_adicional: float
    adicional_dia: bool
    adicional_noche: bool
    codigo_empresa_fk: int
    estado_inactivo: Optional[bool]

    model_config = {"from_attributes": True}


class TurnoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[TurnoResponse]


class TurnoProgramacionRequest(BaseModel):
    turnos: List[str]

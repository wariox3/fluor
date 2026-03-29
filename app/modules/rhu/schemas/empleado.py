from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class EmpleadoBase(BaseModel):
    nombre_corto: str  
    correo: Optional[str]  

class EmpleadoResponse(EmpleadoBase):
    codigo_empleado_pk: int

    class Config:
        from_attributes = True

class EmpleadoResponse(BaseModel):
    codigo_empleado_pk: int
    nombre_corto: str
    numero_identificacion: str
    correo: Optional[str]

    model_config = {"from_attributes": True}


class EmpleadoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[EmpleadoResponse]


class PlazoCredito(BaseModel):
    monto_maximo: float
    cuota: float


class CuotasPorPlazo(BaseModel):
    plazo_12: PlazoCredito
    plazo_24: PlazoCredito
    plazo_36: PlazoCredito


class EstudioCreditoResponse(BaseModel):
    # Identificación
    codigo_empleado_pk: int
    nombre_corto: str
    numero_identificacion: Optional[str]

    # Contrato activo
    contrato_activo: bool
    fecha_inicio_contrato: Optional[date]
    antiguedad_meses: int
    tipo_contrato: Optional[str]

    # Ingresos (promedio últimos 3 pagos aprobados)
    pagos_analizados: int
    ingreso_promedio_devengado: float
    ingreso_promedio_deduccion: float
    ingreso_promedio_neto: float

    # Créditos vigentes
    creditos_vigentes: int
    cuota_mensual_comprometida: float

    # Embargos activos
    embargos_activos: int
    descuento_embargo_mensual: float

    # Capacidad
    porcentaje_aplicado: float
    margen_bruto: float
    cuota_disponible: float
    monto_maximo: CuotasPorPlazo

    # Score
    score: int
    score_detalle: dict
from pydantic import BaseModel
from typing import List, Optional


class ConceptoResponse(BaseModel):
    codigo_concepto_pk: str
    nombre: Optional[str]
    codigo_empresa_fk: Optional[int]
    codigo_concepto_tipo_fk: Optional[str]
    codigo_tipo_electronico_fk: Optional[str]
    codigo_medio_concepto_fk: Optional[int]
    codigo_tercero_fk: Optional[int]
    codigo_cuenta_pagar_tipo_fk: Optional[str]
    porcentaje: Optional[float]
    porcentaje_vacaciones: Optional[float]
    operacion: Optional[int]
    orden: Optional[int]
    numero_dian: Optional[int]
    adicional_tipo: Optional[str]

    # Flags de clasificación
    genera_ingreso_base_prestacion: Optional[bool]
    genera_ingreso_base_cotizacion: Optional[bool]
    genera_ingreso_base_prestacion_vacacion: Optional[bool]
    genera_ingreso_base_prestacion_indemnizacion: Optional[bool]
    adicional: Optional[bool]
    auxilio_transporte: Optional[bool]
    incapacidad: Optional[bool]
    incapacidad_entidad: Optional[bool]
    incapacidad_empresa: Optional[bool]
    pension: Optional[bool]
    salud: Optional[bool]
    vacacion: Optional[bool]
    comision: Optional[bool]
    cesantia: Optional[bool]
    prima: Optional[bool]
    credito: Optional[bool]
    embargo: Optional[bool]
    recargo_nocturno: Optional[bool]
    fondo_solidaridad_pensional: Optional[bool]
    retencion_fuente: Optional[bool]
    anticipo: Optional[bool]
    ingreso_terceros: Optional[bool]
    permiso_adicional: Optional[bool]
    genera_cuenta_pagar: Optional[bool]
    genera_cuenta_pagar_empleado: Optional[bool]
    contabilizar_tercero_entidad_salud: Optional[bool]
    contabilizar_tercero_entidad_pension: Optional[bool]
    contabilizar_tercero_fijo: Optional[bool]
    reconocimiento_incapacidad: Optional[bool]
    salario_suplementario: Optional[bool]
    devengado_deducible: Optional[bool]
    costo: Optional[bool]
    gasto: Optional[bool]

    model_config = {"from_attributes": True}


class ConceptoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ConceptoResponse]

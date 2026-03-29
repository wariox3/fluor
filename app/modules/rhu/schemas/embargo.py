from datetime import date
from pydantic import BaseModel
from typing import List, Optional


class EmbargoResponse(BaseModel):
    codigo_embargo_pk: int
    codigo_embargo_tipo_fk: Optional[str]
    codigo_embargo_juzgado_fk: Optional[str]
    codigo_empleado_fk: Optional[int]
    empleado_nombre: Optional[str]
    codigo_empresa_fk: int
    fecha: Optional[date]
    numero: Optional[str]
    estado_activo: Optional[bool]
    estado_autorizado: Optional[bool]
    estado_aprobado: Optional[bool]
    estado_anulado: Optional[bool]
    valor_fijo: Optional[bool]
    oficina_destino: Optional[str]
    consecutivo_juzgado: Optional[str]
    codigo_instancia: Optional[str]
    porcentaje_devengado: Optional[bool]
    porcentaje_devengado_prestacional: Optional[bool]
    porcentaje_devengado_prestacional_menos_descuento_ley: Optional[bool]
    por_devengado_prestacional_menos_descuento_ley_transporte: Optional[bool]
    porcentaje_devengado_prestacional_menos_transporte: Optional[bool]
    porcentaje_devengado_menos_descuento_ley: Optional[bool]
    porcentaje_devengado_menos_descuento_ley_transporte: Optional[bool]
    porcentaje_exceda_salario_minimo: Optional[bool]
    porcentaje_exceda_salario_minimo_prestacional_menos_transporte: Optional[bool]
    porcentaje_exceda_salario_minimo_prestacional_menos_ley_tte: Optional[bool]
    porcentaje_salario_minimo: Optional[bool]
    partes_exceda_salario_minimo: Optional[bool]
    partes_exceda_salario_minimo_menos_descuento_ley: Optional[bool]
    par_exceda_sal_minimo_prestacional_menos_des_ley: Optional[bool]
    partes: Optional[float]
    vr_valor: Optional[float]
    porcentaje: Optional[float]
    vr_abonos: Optional[float]
    codigo_usuario: Optional[str]
    comentarios: Optional[str]
    cuenta: Optional[str]
    tipo_cuenta: Optional[str]
    numero_expediente: Optional[str]
    numero_proceso: Optional[str]
    numero_radicado: Optional[str]
    oficio: Optional[str]
    oficio_inactivacion: Optional[str]
    fecha_inicio_folio: Optional[date]
    fecha_inactivacion: Optional[date]
    numero_identificacion_demandante: Optional[str]
    nombre_corto_demandante: Optional[str]
    apellidos_demandante: Optional[str]
    numero_identificacion_beneficiario: Optional[str]
    nombre_corto_beneficiario: Optional[str]
    oficina: Optional[str]
    vr_monto_maximo: Optional[float]
    saldo: Optional[float]
    descuento: Optional[float]
    validar_monto_maximo: Optional[bool]
    afecta_nomina: Optional[bool]
    afecta_vacacion: Optional[bool]
    afecta_prima: Optional[bool]
    afecta_liquidacion: Optional[bool]
    afecta_cesantia: Optional[bool]
    afecta_indemnizacion: Optional[bool]
    descontar_novedad: Optional[bool]

    model_config = {"from_attributes": True}


class EmbargoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[EmbargoResponse]

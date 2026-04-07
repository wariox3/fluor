from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import date


class EmpleadoResponse(BaseModel):
    codigo_empleado_pk: int
    nombre_corto: Optional[str]
    numero_identificacion: str
    correo: Optional[str]

    model_config = {"from_attributes": True}


class EmpleadoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[EmpleadoResponse]


class EmpleadoDetalleVencimientoResponse(BaseModel):
    codigo_empleado_pk: int
    fecha_acreditacion: Optional[date] = None
    fecha_poligono: Optional[date] = None
    fecha_psicofisico: Optional[date] = None
    fecha_psicosensometrico: Optional[date] = None

    model_config = {"from_attributes": True}


class EmpleadoDetalleResponse(BaseModel):
    codigo_empleado_pk: int
    # Identificación
    codigo_identificacion_fk: Optional[str] = None
    numero_identificacion: Optional[str] = None
    digito_verificacion: Optional[str] = None
    fecha_expedicion_identificacion: Optional[date] = None
    codigo_ciudad_expedicion_identificacion_fk: Optional[int] = None
    libreta_militar: Optional[str] = None
    distrito_militar: Optional[str] = None
    codigo_libreta_clase_fk: Optional[str] = None
    # Nombres
    nombre_corto: Optional[str] = None
    nombre1: Optional[str] = None
    nombre2: Optional[str] = None
    apellido1: Optional[str] = None
    apellido2: Optional[str] = None
    # Contacto
    telefono: Optional[str] = None
    celular: Optional[str] = None
    correo: Optional[str] = None
    correo_corporativo: Optional[str] = None
    # Datos personales
    fecha_nacimiento: Optional[date] = None
    codigo_ciudad_nacimiento_fk: Optional[int] = None
    codigo_ciudad_fk: Optional[int] = None
    codigo_sexo_fk: Optional[str] = None
    codigo_rh_fk: Optional[str] = None
    codigo_estado_civil_fk: Optional[str] = None
    codigo_raza_fk: Optional[str] = None
    numero_hijos: Optional[int] = None
    # Dirección
    direccion: Optional[str] = None
    barrio: Optional[str] = None
    estrato: Optional[str] = None
    vivienda_tipo: Optional[str] = None
    # Ubicación laboral
    codigo_zona_fk: Optional[str] = None
    codigo_subzona_fk: Optional[str] = None
    codigo_sector_fk: Optional[str] = None
    codigo_departamento_fk: Optional[str] = None
    codigo_segmento_fk: Optional[str] = None
    codigo_estructura_fk: Optional[str] = None
    puesto: Optional[str] = None
    # Contrato
    codigo_contrato_fk: Optional[int] = None
    codigo_contrato_ultimo_fk: Optional[int] = None
    codigo_contrato_registro_fk: Optional[int] = None
    estado_contrato: Optional[bool] = None
    # Banco
    cuenta: Optional[str] = None
    codigo_banco_fk: Optional[str] = None
    codigo_cuenta_tipo_fk: Optional[str] = None
    # Tallas / físico
    talla_camisa: Optional[str] = None
    talla_pantalon: Optional[str] = None
    talla_calzado: Optional[str] = None
    talla_kepis: Optional[str] = None
    estatura: Optional[int] = None
    peso: Optional[int] = None
    # Fechas de seguimiento
    fecha_induccion: Optional[date] = None
    fecha_ultima_reinduccion: Optional[date] = None
    fecha_acreditacion: Optional[date] = None
    fecha_poligono: Optional[date] = None
    fecha_psicofisico: Optional[date] = None
    fecha_psicosensometrico: Optional[date] = None
    fecha_examen_ingreso: Optional[date] = None
    fecha_bloqueo_programacion: Optional[date] = None
    fecha_actualizacion: Optional[date] = None
    # Clasificación social
    codigo_nivel_estudio_fk: Optional[str] = None
    codigo_religion_fk: Optional[str] = None
    religion_otro: Optional[str] = None
    codigo_grupo_voluntariado_fk: Optional[str] = None
    grupo_voluntariado_otro: Optional[str] = None
    codigo_grupo_etnico_fk: Optional[str] = None
    grupo_etnico_otro: Optional[str] = None
    codigo_discapacidad_tipo_fk: Optional[str] = None
    discapacidadtipo_otro: Optional[str] = None
    codigo_permiso_especial_tipo_fk: Optional[str] = None
    permiso_especial: Optional[str] = None
    # Booleans sociales
    discapacidad: Optional[bool] = None
    desplazado: Optional[bool] = None
    victima_conflicto_armado: Optional[bool] = None
    reincorporados: Optional[bool] = None
    afrodescendientes: Optional[bool] = None
    madre_cabeza_familia: Optional[bool] = None
    padre_familia: Optional[bool] = None
    cabeza_hogar: Optional[bool] = None
    lgbt: Optional[bool] = None
    adulto_mayor: Optional[bool] = None
    victima_violencia: Optional[bool] = None
    desplazado_violencia: Optional[bool] = None
    desplazado_fenomeno_natural: Optional[bool] = None
    # Transporte
    carro: Optional[bool] = None
    moto: Optional[bool] = None
    transporte_publico: Optional[bool] = None
    bicicleta: Optional[bool] = None
    # Financiero retención
    vr_pagos_por_salud_prepagada: Optional[float] = None
    vr_interes_vivienda: Optional[float] = None
    vr_retencion_fuente_propuesto: Optional[float] = None
    vr_retencion_fuente_base: Optional[float] = None
    vr_aporte_afc_propuesto: Optional[float] = None
    # Otros
    derecho_dependientes: Optional[bool] = None
    omitir_adicional_puesto: Optional[bool] = None
    codigo_tercero_fk: Optional[int] = None
    codigo_empresa_fk: Optional[int] = None
    codigo_interno: Optional[str] = None
    usuario: Optional[str] = None
    vetado: Optional[bool] = None
    correo_verificado: Optional[bool] = None

    model_config = {"from_attributes": True}


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
from sqlalchemy import Boolean, Column, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class Concepto(Base):
    __tablename__ = "rhu_concepto"

    codigo_concepto_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(80), nullable=True)
    codigo_empresa_fk = Column(Integer)
    codigo_concepto_tipo_fk = Column(String(10), nullable=True)
    codigo_tipo_electronico_fk = Column(String(30), nullable=True)
    codigo_medio_concepto_fk = Column(Integer, nullable=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    codigo_cuenta_pagar_tipo_fk = Column(String(10), nullable=True)
    porcentaje = Column(Float, default=0.0)
    porcentaje_vacaciones = Column(Float, default=0.0, nullable=True)
    operacion = Column(Integer, default=0, nullable=True)
    orden = Column(Integer, default=0, nullable=True)
    numero_dian = Column(Integer, nullable=True)
    adicional_tipo = Column(String(3), nullable=True)  # BON, DES, COM

    # Flags de clasificación
    genera_ingreso_base_prestacion = Column(Boolean, default=False, nullable=True)
    genera_ingreso_base_cotizacion = Column(Boolean, default=False, nullable=True)
    genera_ingreso_base_prestacion_vacacion = Column(Boolean, default=False, nullable=True)
    genera_ingreso_base_prestacion_indemnizacion = Column(Boolean, default=False, nullable=True)
    adicional = Column(Boolean, default=False, nullable=True)
    auxilio_transporte = Column(Boolean, default=False, nullable=True)
    incapacidad = Column(Boolean, default=False, nullable=True)
    incapacidad_entidad = Column(Boolean, default=False, nullable=True)
    incapacidad_empresa = Column(Boolean, default=False, nullable=True)
    pension = Column(Boolean, default=False, nullable=True)
    salud = Column(Boolean, default=False, nullable=True)
    vacacion = Column(Boolean, default=False, nullable=True)
    comision = Column(Boolean, default=False, nullable=True)
    cesantia = Column(Boolean, default=False, nullable=True)
    prima = Column(Boolean, default=False, nullable=True)
    credito = Column(Boolean, default=False, nullable=True)
    embargo = Column(Boolean, default=False, nullable=True)
    recargo_nocturno = Column(Boolean, default=False, nullable=True)
    fondo_solidaridad_pensional = Column(Boolean, default=False, nullable=True)
    retencion_fuente = Column(Boolean, default=False, nullable=True)
    anticipo = Column(Boolean, default=False, nullable=True)
    ingreso_terceros = Column(Boolean, default=False, nullable=True)
    permiso_adicional = Column(Boolean, default=False)
    genera_cuenta_pagar = Column(Boolean, default=False)
    genera_cuenta_pagar_empleado = Column(Boolean, default=False)
    contabilizar_tercero_entidad_salud = Column(Boolean, default=False, nullable=True)
    contabilizar_tercero_entidad_pension = Column(Boolean, default=False, nullable=True)
    contabilizar_tercero_fijo = Column(Boolean, default=False)
    reconocimiento_incapacidad = Column(Boolean, default=False)
    salario_suplementario = Column(Boolean, default=False)
    devengado_deducible = Column(Boolean, default=False)
    costo = Column(Boolean, default=True)
    gasto = Column(Boolean, default=True)

from sqlalchemy import Boolean, Column, Float, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class Adicional(Base):
    __tablename__ = "rhu_adicional"

    codigo_adicional_pk = Column(Integer, primary_key=True, index=True)
    codigo_concepto_fk = Column(String(10), ForeignKey("rhu_concepto.codigo_concepto_pk"))
    codigo_empleado_fk = Column(Integer, ForeignKey("rhu_empleado.codigo_empleado_pk"), index=True)
    codigo_adicional_periodo_fk = Column(Integer, nullable=True)
    codigo_programacion_fk = Column(Integer, nullable=True)
    codigo_programacion_detalle_fk = Column(Integer, nullable=True)
    codigo_contrato_fk = Column(Integer, ForeignKey("rhu_contrato.codigo_contrato_pk"), nullable=True)
    codigo_soporte_contrato_fk = Column(Integer, nullable=True)
    codigo_empresa_fk = Column(Integer)
    fecha = Column(Date, nullable=True)
    fecha_desde = Column(Date, nullable=True)
    fecha_hasta = Column(Date, nullable=True)
    vr_valor = Column(Float, default=0.0)
    horas = Column(Float, default=0.0)
    vr_hora = Column(Float, default=0.0)
    permanente = Column(Boolean, default=False)
    aplica_dia_laborado = Column(Boolean, default=False)
    aplica_dia_laborado_sin_descanso = Column(Boolean, default=False)
    aplica_nomina = Column(Boolean, default=False, nullable=True)
    aplica_prima = Column(Boolean, default=False, nullable=True)
    aplica_cesantia = Column(Boolean, default=False, nullable=True)
    aplica_anticipo = Column(Boolean, default=False)
    detalle = Column(String(250), nullable=True)
    detalle_interno = Column(String(250), nullable=True)
    usuario = Column(String(50), nullable=True)
    estado_inactivo = Column(Boolean, default=False)
    estado_inactivo_periodo = Column(Boolean, default=False)
    estado_autorizado = Column(Boolean, default=False, nullable=True)
    estado_aprobado = Column(Boolean, default=False, nullable=True)
    estado_anulado = Column(Boolean, default=False, nullable=True)
    estado_contabilizado = Column(Boolean, default=False, nullable=True)
    cobrar_cliente = Column(Boolean, default=False)
    vr_cobrar_cliente = Column(Float, default=0.0)

    concepto_rel = relationship("Concepto", foreign_keys=[codigo_concepto_fk])
    empleado_rel = relationship("Empleado", foreign_keys=[codigo_empleado_fk])
    contrato_rel = relationship("Contrato", foreign_keys=[codigo_contrato_fk])

    @property
    def concepto_nombre(self) -> str | None:
        return self.concepto_rel.nombre if self.concepto_rel else None

    @property
    def empleado_nombre(self) -> str | None:
        return self.empleado_rel.nombre_corto if self.empleado_rel else None

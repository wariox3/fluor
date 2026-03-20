from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base

class Pago(Base):
    __tablename__ = "rhu_pago"

    codigo_pago_pk = Column(Integer, primary_key=True, index=True)
    codigo_empleado_fk = Column(Integer, ForeignKey("rhu_empleado.codigo_empleado_pk"), index=True)
    codigo_pago_tipo_fk = Column(String(10), ForeignKey("rhu_pago_tipo.codigo_pago_tipo_pk"), index=True, nullable=True)
    numero = Column(Integer)
    fecha_desde = Column(Date)
    fecha_hasta = Column(Date)
    vr_salario_contrato = Column(Float)
    vr_devengado = Column(Float)
    vr_deduccion = Column(Float)
    vr_neto = Column(Float)
    estado_autorizado = Column(Boolean, default=False)
    estado_aprobado = Column(Boolean, default=False)
    estado_anulado = Column(Boolean, default=False)
    habilitado_portal = Column(Boolean, default=True)

    pago_tipo = relationship("PagoTipo", foreign_keys=[codigo_pago_tipo_fk], primaryjoin="Pago.codigo_pago_tipo_fk == PagoTipo.codigo_pago_tipo_pk")
    empleado = relationship("Empleado", foreign_keys=[codigo_empleado_fk], primaryjoin="Pago.codigo_empleado_fk == Empleado.codigo_empleado_pk")

    @property
    def pago_tipo_nombre(self) -> str | None:
        return self.pago_tipo.nombre if self.pago_tipo else None

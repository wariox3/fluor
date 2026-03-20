from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Numeric, Float
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base

class Reclamo(Base):
    __tablename__ = "rhu_reclamo"

    codigo_reclamo_pk = Column(Integer, primary_key=True, index=True)
    codigo_empleado_fk = Column(Integer, ForeignKey("rhu_empleado.codigo_empleado_pk"), index=True)
    codigo_reclamo_concepto_fk = Column(String(10), ForeignKey("rhu_reclamo_concepto.codigo_reclamo_concepto_pk"), index=True, nullable=True)
    fecha = Column(Date)
    fecha_cierre = Column(Date)
    descripcion = Column(String(2000), nullable=False)
    estado_autorizado = Column(Boolean, default=False)
    estado_aprobado = Column(Boolean, default=False)
    estado_anulado = Column(Boolean, default=False)
    estado_cerrado = Column(Boolean, default=False)
    estado_atendido = Column(Boolean, default=False)
    cantidad_respuestas = Column(Integer, default=0)
    codigo_empresa_fk = Column(Integer)
    usuario = Column(String(50), nullable=True)

    reclamo_concepto = relationship("ReclamoConcepto", foreign_keys=[codigo_reclamo_concepto_fk])

    @property
    def reclamo_concepto_nombre(self) -> str | None:
        return self.reclamo_concepto.nombre if self.reclamo_concepto else None


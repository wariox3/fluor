from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.tenant_database import Base


class AporteContrato(Base):
    """Línea de la planilla de seguridad social: un contrato dentro de un aporte."""

    __tablename__ = "rhu_aporte_contrato"

    codigo_aporte_contrato_pk = Column(Integer, primary_key=True, index=True)
    codigo_aporte_fk = Column(Integer, ForeignKey("rhu_aporte.codigo_aporte_pk"), nullable=False, index=True)
    codigo_contrato_fk = Column(Integer, ForeignKey("rhu_contrato.codigo_contrato_pk"), nullable=False, index=True)
    codigo_empleado_fk = Column(Integer, ForeignKey("rhu_empleado.codigo_empleado_pk"), nullable=True, index=True)
    dias = Column(Integer, nullable=False, default=0)
    vr_salario = Column(Float, nullable=False, default=0)
    ibc = Column(Float, nullable=False, default=0)

    aporte_rel = relationship("Aporte", foreign_keys=[codigo_aporte_fk])
    contrato_rel = relationship("Contrato", foreign_keys=[codigo_contrato_fk])
    empleado_rel = relationship("Empleado", foreign_keys=[codigo_empleado_fk])

    @property
    def empleado_nombre(self) -> str | None:
        return self.empleado_rel.nombre_corto if self.empleado_rel else None

    @property
    def numero_identificacion(self) -> str | None:
        return self.empleado_rel.numero_identificacion if self.empleado_rel else None

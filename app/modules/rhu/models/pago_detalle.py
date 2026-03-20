from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.rhu.models.concepto import Concepto  # noqa: F401


class PagoDetalle(Base):
    __tablename__ = "rhu_pago_detalle"

    codigo_pago_detalle_pk = Column(Integer, primary_key=True, index=True)
    codigo_pago_fk = Column(Integer, ForeignKey("rhu_pago.codigo_pago_pk"), nullable=False, index=True)
    codigo_concepto_fk = Column(String(10), ForeignKey("rhu_concepto.codigo_concepto_pk"), nullable=True)
    detalle = Column(String(500), nullable=True)
    porcentaje = Column(Float, nullable=True)
    horas = Column(Float, nullable=True)
    dias = Column(Float, nullable=True)
    vr_hora = Column(Float, nullable=True)
    operacion = Column(String(1), nullable=True)
    vr_pago = Column(Float, nullable=True)
    vr_devengado = Column(Float, nullable=True)
    vr_deduccion = Column(Float, nullable=True)
    vr_pago_operado = Column(Float, nullable=True)
    vr_ingreso_base_prestacion = Column(Float, nullable=True)
    vr_ingreso_base_cotizacion = Column(Float, nullable=True)

    concepto = relationship("Concepto", foreign_keys=[codigo_concepto_fk])

    @property
    def concepto_nombre(self) -> str | None:
        return self.concepto.nombre if self.concepto else None

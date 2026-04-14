from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class FinSaldoCentroCosto(Base):
    __tablename__ = "fin_saldo_centro_costo"

    codigo_periodo_fk = Column(Integer, ForeignKey("fin_periodo.codigo_periodo_pk"), primary_key=True)
    codigo_cuenta_fk = Column(String(20), ForeignKey("fin_cuenta.codigo_cuenta_pk"), primary_key=True)
    codigo_centro_costo_fk = Column(String(20), ForeignKey("fin_centro_costo.codigo_centro_costo_pk"), primary_key=True)

    vr_debito = Column(Float, nullable=False, default=0.0)
    vr_credito = Column(Float, nullable=False, default=0.0)

    periodo_rel = relationship("FinPeriodo", foreign_keys=[codigo_periodo_fk])
    cuenta_rel = relationship("FinCuenta", foreign_keys=[codigo_cuenta_fk])
    centro_costo_rel = relationship("FinCentroCosto", foreign_keys=[codigo_centro_costo_fk])

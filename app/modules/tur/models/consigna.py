from sqlalchemy import Boolean, Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class Consigna(Base):
    __tablename__ = "tur_consigna"

    codigo_consigna_pk = Column(Integer, primary_key=True, index=True)
    codigo_puesto_fk = Column(Integer, ForeignKey("tur_puesto.codigo_puesto_pk"), nullable=True, index=True)
    codigo_empresa_fk = Column(Integer)
    consigna = Column(Text, nullable=True)
    habilitado_portal = Column(Boolean, default=True, nullable=True)

    puesto_rel = relationship("Puesto", foreign_keys=[codigo_puesto_fk])

    @property
    def puesto_nombre(self) -> str | None:
        return self.puesto_rel.nombre if self.puesto_rel else None

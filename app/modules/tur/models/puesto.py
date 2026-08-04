from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class Puesto(Base):
    __tablename__ = "tur_puesto"

    codigo_puesto_pk = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(300))
    nombre_corto = Column(String(300))
    codigo_zona_fk = Column(String(20), ForeignKey("tur_zona.codigo_zona_pk"), nullable=True)
    codigo_subzona_fk = Column(String(20), ForeignKey("tur_subzona.codigo_subzona_pk"), nullable=True)

    zona_rel = relationship("TurZona", foreign_keys=[codigo_zona_fk])
    subzona_rel = relationship("TurSubzona", foreign_keys=[codigo_subzona_fk])

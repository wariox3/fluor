from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.tte.models.despacho import Despacho
from app.modules.tte.models.guia import Guia


class Ubicacion(Base):
    __tablename__ = "tte_ubicacion"

    codigo_ubicacion_pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_despacho_fk = Column(Integer, ForeignKey("tte_despacho.codigo_despacho_pk"), nullable=True)
    codigo_guia_fk = Column(Integer, ForeignKey("tte_guia.codigo_guia_pk"), nullable=True)
    fecha = Column(DateTime, nullable=True)
    usuario = Column(String(25), nullable=True)
    latitud = Column(Float, nullable=True, default=0.0)
    longitud = Column(Float, nullable=True, default=0.0)
    velocidad = Column(Float, nullable=True, default=0.0)
    altitud = Column(Float, nullable=True, default=0.0)
    exactitud = Column(Float, nullable=True, default=0.0)
    exactitud_altitud = Column(Float, nullable=True, default=0.0)

    # Relaciones
    despacho = relationship(Despacho, backref="ubicaciones_despacho")
    guia = relationship(Guia, backref="ubicaciones_guia")

from sqlalchemy import Column, Float, String
from app.core.tenant_database import Base


class Modalidad(Base):
    __tablename__ = "tur_modalidad"

    codigo_modalidad_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(120))
    # Incremento sobre el valor base del servicio al cotizar, según el sector
    porcentaje = Column(Float, nullable=True, default=0)
    porcentaje_residencial = Column(Float, nullable=True, default=10)

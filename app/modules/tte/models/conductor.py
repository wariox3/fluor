from sqlalchemy import Column, Integer, String
from app.core.tenant_database import Base


class Conductor(Base):
    __tablename__ = "tte_conductor"

    codigo_conductor_pk = Column(Integer, primary_key=True, index=True)
    numero_identificacion = Column(String(20), nullable=True)
    nombre_corto = Column(String(150), nullable=True)

from sqlalchemy import Column, String
from app.core.tenant_database import Base


class Modalidad(Base):
    __tablename__ = "tur_modalidad"

    codigo_modalidad_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(120))

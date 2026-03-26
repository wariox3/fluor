from sqlalchemy import Column, Integer, String
from app.core.tenant_database import Base


class Puesto(Base):
    __tablename__ = "tur_puesto"

    codigo_puesto_pk = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(300))
    nombre_corto = Column(String(300))

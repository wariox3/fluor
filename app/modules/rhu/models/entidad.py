from sqlalchemy import Column, Integer, String
from app.core.tenant_database import Base


class Entidad(Base):
    __tablename__ = "rhu_entidad"

    codigo_entidad_pk = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200))
    nombre_corto = Column(String(100))

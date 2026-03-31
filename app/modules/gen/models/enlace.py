from sqlalchemy import Column, Integer, String, DateTime
from app.core.tenant_database import Base


class Enlace(Base):
    __tablename__ = "gen_enlace"

    codigo_enlace_pk = Column(Integer, primary_key=True, index=True)
    codigo_modelo_fk = Column(String(50), nullable=True)
    codigo_documento = Column(Integer, nullable=True)
    url = Column(String(1000), nullable=True)
    nombre = Column(String(200), nullable=True)
    usuario = Column(String(50), nullable=True)
    descripcion = Column(String(500), nullable=True)
    fecha = Column(DateTime, nullable=True)

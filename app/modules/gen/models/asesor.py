from sqlalchemy import Column, Integer, String, Boolean
from app.core.tenant_database import Base


class Asesor(Base):
    __tablename__ = "gen_asesor"

    codigo_asesor_pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    numero_identificacion = Column(String(15), nullable=False)
    nombre = Column(String(80), nullable=True)
    direccion = Column(String(80), nullable=True)
    telefono = Column(String(20), nullable=True)
    celular = Column(String(20), nullable=True)
    email = Column(String(80), nullable=True)
    estado_inactivo = Column(Boolean, nullable=False, default=False)

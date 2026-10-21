from sqlalchemy import Column, Integer, String

from app.core.tenant_database import Base


class Departamento(Base):
    __tablename__ = "tte_departamento"

    codigo_departamento_pk = Column(String(2), primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)

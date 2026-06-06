from sqlalchemy import Boolean, Column, Integer, String
from app.core.tenant_database import Base


class NovedadTipo(Base):
    __tablename__ = "tte_novedad_tipo"

    codigo_novedad_tipo_pk = Column(String(20), primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)
    interna = Column(Boolean, nullable=True, default=False)
    aplica_movil = Column(Boolean, nullable=True, default=False)
    codigo_empresa_fk = Column(Integer, nullable=False)
    codigo_interface = Column(String(50), nullable=True)

from sqlalchemy import Column, String
from app.core.tenant_database import Base


class SeguimientoTipo(Base):
    __tablename__ = "tte_seguimiento_tipo"

    codigo_seguimiento_tipo_pk = Column(String(30), primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)

from sqlalchemy import Boolean, Column, String
from app.core.tenant_database import Base


class TurZona(Base):
    __tablename__ = "tur_zona"

    codigo_zona_pk = Column(String(20), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    estado_inactivo = Column(Boolean, default=False)

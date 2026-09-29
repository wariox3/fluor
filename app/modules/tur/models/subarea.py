from sqlalchemy import Column, String
from app.core.tenant_database import Base


class TurSubarea(Base):
    __tablename__ = "tur_subarea"

    codigo_subarea_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(80), nullable=False)

from sqlalchemy import Column, String
from app.core.tenant_database import Base


class Zona(Base):
    __tablename__ = "rhu_zona"

    codigo_zona_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(200))

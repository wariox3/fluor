from sqlalchemy import Boolean, Column, Float, String

from app.core.tenant_database import Base


class Sector(Base):
    """Sector del servicio cotizado (comercial, residencial…); su porcentaje sube el valor base."""

    __tablename__ = "tur_sector"

    codigo_sector_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)
    porcentaje = Column(Float, nullable=True)
    estado_inactivo = Column(Boolean, nullable=False, default=False)

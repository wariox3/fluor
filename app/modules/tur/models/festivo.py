from sqlalchemy import Column, Date, String

from app.core.tenant_database import Base


class Festivo(Base):
    """Día festivo del calendario de la empresa."""

    __tablename__ = "tur_festivo"

    codigo_festivo_pk = Column(String(8), primary_key=True, index=True)
    fecha = Column(Date, nullable=True)

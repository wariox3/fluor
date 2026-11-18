from sqlalchemy import Column, Date, ForeignKey, Integer, Text

from app.core.tenant_database import Base


class SolicitudAnalisis(Base):
    """Análisis de causa que la empresa registra a una PQRS en holmio."""

    __tablename__ = "crm_solicitud_analisis"

    codigo_solicitud_analisis_pk = Column(Integer, primary_key=True, index=True)
    codigo_solicitud_fk = Column(Integer, ForeignKey("crm_solicitud.codigo_solicitud_pk"), nullable=True, index=True)
    # FK sin modelo local
    codigo_analisis_causa_fk = Column(Integer, nullable=True)
    fecha = Column(Date, nullable=True)
    razon = Column(Text, nullable=True)
    causa_raiz = Column(Text, nullable=True)

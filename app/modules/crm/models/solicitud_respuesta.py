from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.core.tenant_database import Base


class SolicitudRespuesta(Base):
    """Respuesta que la empresa da a una PQRS en holmio."""

    __tablename__ = "crm_solicitud_respuesta"

    codigo_solicitud_respuesta_pk = Column(Integer, primary_key=True, index=True)
    codigo_solicitud_fk = Column(Integer, ForeignKey("crm_solicitud.codigo_solicitud_pk"), nullable=True, index=True)
    codigo_canal_fk = Column(String(10), nullable=True)
    respuesta = Column(Text, nullable=True)
    fecha = Column(DateTime, nullable=True)
    fecha_respuesta = Column(DateTime, nullable=True)

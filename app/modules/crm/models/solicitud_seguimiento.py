from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text

from app.core.tenant_database import Base


class SolicitudSeguimiento(Base):
    """Seguimiento (plan de acción) que la empresa registra a una PQRS en holmio."""

    __tablename__ = "crm_solicitud_seguimiento"

    codigo_solicitud_seguimiento_pk = Column(Integer, primary_key=True, index=True)
    codigo_solicitud_fk = Column(Integer, ForeignKey("crm_solicitud.codigo_solicitud_pk"), nullable=True, index=True)

    # FKs sin modelo local
    codigo_area_fk = Column(String(10), nullable=True)
    codigo_causal_fk = Column(String(10), nullable=True)

    fecha = Column(Date, nullable=True)
    plan_accion = Column(Text, nullable=True)
    descripcion = Column(Text, nullable=True)
    responsable = Column(String(200), nullable=True)
    responsable_atencion = Column(String(200), nullable=True)
    descripcion_atencion = Column(Text, nullable=True)

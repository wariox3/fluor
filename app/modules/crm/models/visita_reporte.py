from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.core.tenant_database import Base


class VisitaReporte(Base):
    __tablename__ = "crm_visita_reporte"

    codigo_visita_reporte_pk = Column(Integer, primary_key=True, index=True)
    codigo_visita_fk = Column(Integer, ForeignKey("crm_visita.codigo_visita_pk"), nullable=True, index=True)
    fecha = Column(DateTime, nullable=False)
    nombre_contacto = Column(String(100), nullable=True)
    cargo = Column(String(100), nullable=True)
    reporte = Column(Text, nullable=True)

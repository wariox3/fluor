from sqlalchemy import Column, String

from app.core.tenant_database import Base


class VisitaMotivo(Base):
    __tablename__ = "crm_visita_motivo"

    codigo_visita_motivo_pk = Column(String(20), primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)

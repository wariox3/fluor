from sqlalchemy import Column, String

from app.core.tenant_database import Base


class VisitaTipo(Base):
    __tablename__ = "crm_visita_tipo"

    codigo_visita_tipo_pk = Column(String(20), primary_key=True, index=True)
    nombre = Column(String(80), nullable=False)

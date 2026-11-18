from sqlalchemy import Boolean, Column, Integer, String

from app.core.tenant_database import Base


class SolicitudTema(Base):
    """Tema con el que quien gestiona la PQRS la clasifica en holmio."""

    __tablename__ = "crm_solicitud_tema"

    codigo_solicitud_tema_pk = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    portal_clientes = Column(Boolean, nullable=False, default=False)

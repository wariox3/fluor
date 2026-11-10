from sqlalchemy import Boolean, Column, String

from app.core.tenant_database import Base


class SolicitudTipo(Base):
    __tablename__ = "crm_solicitud_tipo"

    codigo_solicitud_tipo_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    # Si el cliente puede registrar este tipo de solicitud desde el portal
    portal_clientes = Column(Boolean, nullable=False, default=False)

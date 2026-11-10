from sqlalchemy import Boolean, Column, String

from app.core.tenant_database import Base


class Canal(Base):
    __tablename__ = "crm_canal"

    codigo_canal_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    # En qué registros del CRM se puede usar el canal
    negocio = Column(Boolean, nullable=False, default=False)
    solicitud = Column(Boolean, nullable=False, default=False)
    respuesta = Column(Boolean, nullable=False, default=False)

from sqlalchemy import Boolean, Column, Integer, String

from app.core.tenant_database import Base


class CotizacionTipo(Base):
    __tablename__ = "crm_cotizacion_tipo"

    codigo_cotizacion_tipo_pk = Column(String(10), primary_key=True, index=True)

    # FKs sin modelo local
    codigo_cotizacion_clase_fk = Column(String(10), nullable=True)

    nombre = Column(String(255), nullable=False)
    consecutivo = Column(Integer, nullable=True, default=0)
    # Si el cliente puede cotizar este tipo desde el portal
    portal_clientes = Column(Boolean, nullable=False, default=False)
    formato = Column(String(10), nullable=True)

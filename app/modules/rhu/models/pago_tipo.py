from sqlalchemy import Boolean, Column, String
from app.core.tenant_database import Base

class PagoTipo(Base):
    __tablename__ = "rhu_pago_tipo"

    codigo_pago_tipo_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(80), nullable=False)
    habilitado_portal = Column(Boolean, default=True)

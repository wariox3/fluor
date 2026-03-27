from sqlalchemy import Column, String
from app.core.tenant_database import Base


class ContratoTipo(Base):
    __tablename__ = "rhu_contrato_tipo"

    codigo_contrato_tipo_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(200))

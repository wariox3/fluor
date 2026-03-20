from sqlalchemy import Column, String
from app.core.tenant_database import Base


class Concepto(Base):
    __tablename__ = "rhu_concepto"

    codigo_concepto_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(80), nullable=False)

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Numeric, Float
from app.core.tenant_database import Base

class ReclamoConcepto(Base):
    __tablename__ = "rhu_reclamo_concepto"

    codigo_reclamo_concepto_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(80), nullable=False)
    portal_empleados          = Column(Boolean, default=True)


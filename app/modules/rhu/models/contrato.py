from sqlalchemy import Column, Float, Integer, String, Date, Numeric
from app.core.tenant_database import Base

class Contrato(Base):
    __tablename__ = "rhu_contrato"

    codigo_contrato_pk = Column(Integer, primary_key=True, index=True)
    codigo_empleado_fk = Column(Integer, index=True)
    fecha_desde = Column(Date)
    fecha_hasta = Column(Date)
    vr_salario = Column(Float)
    

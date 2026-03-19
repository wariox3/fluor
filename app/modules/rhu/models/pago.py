from sqlalchemy import Column, Float, Integer, String, Date, Numeric
from app.core.tenant_database import Base

class Pago(Base):
    __tablename__ = "rhu_pago"

    codigo_pago_pk = Column(Integer, primary_key=True, index=True)
    codigo_empleado_fk = Column(Integer, index=True)
    fecha_desde = Column(Date)
    fecha_hasta = Column(Date)
    vr_salario_contrato = Column(Float)
    vr_devengado = Column(Float)
    vr_deduccion = Column(Float)
    vr_neto = Column(Float)

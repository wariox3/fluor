from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Numeric, Float
from app.core.tenant_database import Base

class Reclamo(Base):
    __tablename__ = "rhu_reclamo"

    codigo_reclamo_pk = Column(Integer, primary_key=True, index=True)
    codigo_empleado_fk = Column(Integer, index=True)
    fecha = Column(Date)
    fecha_cierre = Column(Date)
    descripcion = Column(String(2000), nullable=False)
    estado_autorizado = Column(Boolean, default=False)
    estado_aprobado = Column(Boolean, default=False)
    estado_anulado = Column(Boolean, default=False)
    estado_cerrado = Column(Boolean, default=False)
    estado_atendido = Column(Boolean, default=False)
    cantidad_respuestas = Column(Integer, default=0)


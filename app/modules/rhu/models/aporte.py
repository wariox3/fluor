from sqlalchemy import Boolean, Column, Date, Float, Integer, String

from app.core.tenant_database import Base


class Aporte(Base):
    """Planilla de seguridad social (PILA) de un periodo."""

    __tablename__ = "rhu_aporte"

    codigo_aporte_pk = Column(Integer, primary_key=True, index=True)
    codigo_aporte_tipo_fk = Column(String(10), nullable=True)
    codigo_sucursal_fk = Column(String(10), nullable=True)
    numero = Column(Integer, nullable=True)
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    fecha_desde = Column(Date, nullable=False)
    fecha_hasta = Column(Date, nullable=False)
    cantidad_contratos = Column(Integer, nullable=True)
    cantidad_empleados = Column(Integer, nullable=True)
    vr_total = Column(Float, nullable=True)
    estado_autorizado = Column(Boolean, nullable=False, default=False)
    estado_aprobado = Column(Boolean, nullable=True, default=False)
    estado_anulado = Column(Boolean, nullable=True, default=False)

from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.rhu.models.capacitacion import Capacitacion
from app.modules.rhu.models.empleado import Empleado


class CapacitacionDetalle(Base):
    __tablename__ = "rhu_capacitacion_detalle"

    codigo_capacitacion_detalle_pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_capacitacion_fk = Column(Integer, ForeignKey("rhu_capacitacion.codigo_capacitacion_pk"), nullable=True, index=True)
    codigo_empleado_fk = Column(Integer, ForeignKey("rhu_empleado.codigo_empleado_pk"), nullable=False, index=True)
    numero_identificacion = Column(String(50), nullable=True)
    nombre_corto = Column(String(80), nullable=True)
    asistencia = Column(Boolean, default=False, nullable=False)
    evaluacion = Column(String(80), nullable=True)
    ip_confirmacion_usuario = Column(String(80), nullable=True)
    fecha_confirmacion_usuario = Column(DateTime, nullable=True)

    capacitacion_rel = relationship("Capacitacion", foreign_keys=[codigo_capacitacion_fk])
    empleado_rel = relationship("Empleado", foreign_keys=[codigo_empleado_fk])

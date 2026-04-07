from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class EmpleadoActualizacion(Base):
    __tablename__ = "rhu_empleado_actualizacion"

    codigo_empleado_actualizacion_pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_empleado_fk = Column(Integer, ForeignKey("rhu_empleado.codigo_empleado_pk"), nullable=False, index=True)
    codigo_ciudad_fk = Column(Integer, ForeignKey("gen_ciudad.codigo_ciudad_pk"), nullable=True)
    celular = Column(String(20), nullable=True)
    telefono = Column(String(100), nullable=True)
    direccion = Column(String(120), nullable=True)
    barrio = Column(String(100), nullable=True)
    correo = Column(String(80), nullable=True)
    fecha = Column(Date, nullable=True)
    estado_aplicado = Column(Boolean, default=False, nullable=True)

    empleado_rel = relationship("Empleado", foreign_keys=[codigo_empleado_fk])
    ciudad_rel = relationship("Ciudad", foreign_keys=[codigo_ciudad_fk])

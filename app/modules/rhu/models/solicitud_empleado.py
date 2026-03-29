from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.rhu.models.solicitud_empleado_tipo import SolicitudEmpleadoTipo


class SolicitudEmpleado(Base):
    __tablename__ = "rhu_solicitud_empleado"

    codigo_solicitud_empleado_pk = Column(Integer, primary_key=True, index=True)
    codigo_empleado_fk = Column(Integer, ForeignKey("rhu_empleado.codigo_empleado_pk"), index=True)
    codigo_solicitud_empleado_tipo_fk = Column(String(10), ForeignKey("rhu_solicitud_empleado_tipo.codigo_solicitud_empleado_tipo_pk"), nullable=True, index=True)
    fecha_registro = Column(Date, nullable=True)
    fecha_desde = Column(DateTime, nullable=True)
    fecha_hasta = Column(DateTime, nullable=True)
    comentario = Column(Text, nullable=True)
    usuario = Column(String(50), nullable=True)
    comentario_rechazo = Column(String(500), nullable=True)
    estado_autorizado = Column(Boolean, default=False, nullable=True)
    estado_aprobado = Column(Boolean, default=False, nullable=True)
    estado_anulado = Column(Boolean, default=False, nullable=True)
    estado_cerrado = Column(Boolean, default=False, nullable=True)
    estado_solicitud = Column(String(1), default="P", nullable=True)
    codigo_empresa_fk = Column(Integer)

    solicitud_empleado_tipo = relationship("SolicitudEmpleadoTipo", foreign_keys=[codigo_solicitud_empleado_tipo_fk])

    @property
    def solicitud_empleado_tipo_nombre(self) -> str | None:
        return self.solicitud_empleado_tipo.nombre if self.solicitud_empleado_tipo else None

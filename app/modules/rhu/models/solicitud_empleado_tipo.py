from sqlalchemy import Boolean, Column, String
from app.core.tenant_database import Base


class SolicitudEmpleadoTipo(Base):
    __tablename__ = "rhu_solicitud_empleado_tipo"

    codigo_solicitud_empleado_tipo_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(80), nullable=True)
    habilitado_portal = Column(Boolean, default=True, nullable=True)

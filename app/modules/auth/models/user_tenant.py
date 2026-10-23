import enum
from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer, UniqueConstraint, func, true)
from sqlalchemy.orm import relationship
from app.core.master_database import Base


class TenantRole(str, enum.Enum):
    """Rol de un usuario dentro de una empresa. El rol global (admin) vive en user.role."""
    control = "control"
    user = "user"
    viewer = "viewer"
    employee = "employee"


class UserTenant(Base):
    """Acceso de un usuario a una empresa, con su rol y empleado en esa empresa."""
    __tablename__ = "user_tenant"
    __table_args__ = (UniqueConstraint("usuario_id", "tenant_id", name="uq_user_tenant_usuario_tenant"),)

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False, index=True)
    role = Column(Enum(TenantRole), nullable=False)
    empleado_id = Column(Integer, nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default=true())
    fecha_creacion = Column(DateTime, server_default=func.now(), nullable=False)

    usuario = relationship("User", back_populates="users_tenants")
    tenant = relationship("Tenant", back_populates="users_tenants")

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, UniqueConstraint, false, func, true)
from sqlalchemy.orm import Session, relationship
from app.core.master_database import Base


class UserTenant(Base):
    """Acceso de un usuario a una empresa, con su empleado en esa empresa."""
    __tablename__ = "mas_user_tenant"
    __table_args__ = (UniqueConstraint("usuario_id", "tenant_id", name="uq_user_tenant_usuario_tenant"),)

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("auth_user.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("mas_tenant.id"), nullable=False, index=True)
    empleado_id = Column(Integer, nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default=true())
    control = Column(Boolean, nullable=False, default=False, server_default=false())
    fecha_creacion = Column(DateTime, server_default=func.now(), nullable=False)

    usuario = relationship("User", back_populates="users_tenants")
    tenant = relationship("Tenant", back_populates="users_tenants")


def es_control(db: Session, usuario_id: int, tenant_id: int) -> bool:
    """True si el usuario es control activo en la empresa."""
    return db.query(UserTenant.id).filter(
        UserTenant.usuario_id == usuario_id,
        UserTenant.tenant_id == tenant_id,
        UserTenant.activo == True,
        UserTenant.control == True,
    ).first() is not None

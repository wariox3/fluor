import enum
from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, func, true)
from sqlalchemy.orm import relationship
from app.core.master_database import Base
from app.modules.mas.models.tenant import Tenant
from app.modules.mas.models.user_tenant import UserTenant  # noqa: F401 — registra el modelo para la relación

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"
    viewer = "viewer"
    control = "control"
    employee = "employee"

class User(Base):
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    tenant_id = Column(Integer, ForeignKey("mas_tenant.id"), nullable=True)
    nombres = Column(String(150), nullable=True)
    apellidos = Column(String(150), nullable=True)
    numero_identificacion = Column(String(50), nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default=true())
    empleado_id = Column(Integer, nullable=True)
    codigo_usuario_fk = Column(String(25), nullable=True)
    fecha_creacion = Column(DateTime, server_default=func.now(), nullable=False)

    tenant = relationship(Tenant, back_populates="users")
    users_tenants = relationship("UserTenant", back_populates="usuario")


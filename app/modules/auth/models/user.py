import enum
from sqlalchemy import (Column, Enum, ForeignKey, Integer, String)
from sqlalchemy.orm import relationship
from app.core.master_database import Base
from app.modules.auth.models.tenant import Tenant

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"
    viewer = "viewer"
    control = "control"
    employee = "employee"

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=True)
    nombres = Column(String(150), nullable=True)
    apellidos = Column(String(150), nullable=True)
    numero_identificacion = Column(String(50), nullable=True)

    tenant = relationship(Tenant, back_populates="users")


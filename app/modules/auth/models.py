import enum
from datetime import datetime, timezone
from sqlalchemy import (Column, DateTime, Enum, ForeignKey, Integer, String, Boolean, func)
from sqlalchemy.orm import relationship
from app.core.master_database import Base

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"
    viewer = "viewer"
    control = "control"

class Tenant(Base):
    __tablename__ = "tenant"

    id = Column(Integer, primary_key=True, index=True)    
    nombre = Column(String(100))
    schema = Column(String(100))

    users = relationship("User", back_populates="tenant")
    api_keys = relationship("ApiKey", back_populates="tenant")

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)    
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=True)

    tenant = relationship(Tenant, back_populates="users")


class ApiKey(Base):
    __tablename__ = "api_key"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    key_hash = Column(String(255), unique=True, index=True)
    prefix = Column(String(20))
    is_active = Column(Boolean, default=True)    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False)

    tenant = relationship(Tenant, back_populates="api_keys")


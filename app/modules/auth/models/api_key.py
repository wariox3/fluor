from datetime import datetime, timezone
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, Boolean)
from sqlalchemy.orm import relationship
from app.core.master_database import Base
from app.modules.auth.models.tenant import Tenant

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


from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.master_database import Base


class Notificacion(Base):
    __tablename__ = "notificacion"

    id              = Column(Integer, primary_key=True, index=True)
    usuario_id      = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    tipo            = Column(String(50), nullable=False)
    titulo          = Column(String(150), nullable=False)
    mensaje         = Column(Text, nullable=True)
    url             = Column(String(255), nullable=True)
    leida           = Column(Boolean, default=False, server_default="0", nullable=False)
    fecha_creacion  = Column(DateTime, default=datetime.utcnow, nullable=False)

    usuario = relationship("User", foreign_keys=[usuario_id])

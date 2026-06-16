import enum
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.master_database import Base


class TipoVerificacion(str, enum.Enum):
    registro = "registro"          # token de verificación creado al registrarse
    reenvio = "reenvio"            # token de verificación reenviado
    recuperacion = "recuperacion"  # token de recuperación de clave


class EstadoVerificacion(str, enum.Enum):
    pendiente = "pendiente"  # token vigente, aún no consumido
    usado = "usado"          # token consumido correctamente


class Verificacion(Base):
    __tablename__ = "verificacion"

    id             = Column(Integer, primary_key=True, index=True)
    usuario_id     = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    tipo           = Column(Enum(TipoVerificacion), nullable=False)
    token          = Column(String(64), nullable=False, unique=True, index=True)
    estado         = Column(Enum(EstadoVerificacion), nullable=False, default=EstadoVerificacion.pendiente)
    ip             = Column(String(45), nullable=True)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    fecha_uso      = Column(DateTime, nullable=True)

    usuario = relationship("User", foreign_keys=[usuario_id])

import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, func
from app.core.master_database import Base


class EstadoInvitacion(str, enum.Enum):
    pendiente = "pendiente"
    aceptada = "aceptada"
    rechazada = "rechazada"
    cancelada = "cancelada"


class Invitacion(Base):
    """Invitación de un usuario a otro (registrado y verificado) para unirse a una empresa."""
    __tablename__ = "invitacion"

    id                  = Column(Integer, primary_key=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.id"), nullable=False, index=True)
    # Quien invita; si se elimina, la invitación se conserva sin autor
    usuario_id          = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)
    # El invitado; si se elimina, sus invitaciones dejan de tener sentido
    usuario_invitado_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    estado              = Column(Enum(EstadoInvitacion), nullable=False, default=EstadoInvitacion.pendiente, server_default=EstadoInvitacion.pendiente.value)
    fecha               = Column(DateTime, server_default=func.now(), nullable=False)

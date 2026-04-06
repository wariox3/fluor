from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.master_database import Base


class CreditoSolicitud(Base):
    __tablename__ = "mas_credito_solicitud"

    codigo_credito_solicitud_pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    monto = Column(Numeric(18, 2), nullable=False)
    plazo = Column(Integer, nullable=False)                          # en meses
    tasa_interes = Column(Numeric(5, 2), nullable=True)              # % anual
    descripcion = Column(Text, nullable=True)
    estado = Column(String(20), nullable=False, default="pendiente") # pendiente, aprobado, rechazado, desembolsado
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_actualizacion = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    usuario = relationship("User", lazy="joined")


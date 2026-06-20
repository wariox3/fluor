from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.tte.models.monitoreo import Monitoreo
from app.modules.tte.models.monitoreo_seguimiento import MonitoreoSeguimiento


class MonitoreoDetalle(Base):
    __tablename__ = "tte_monitoreo_detalle"

    codigo_monitoreo_detalle_pk = Column(Integer, primary_key=True, index=True)

    # FKs
    codigo_monitoreo_fk = Column(Integer, ForeignKey("tte_monitoreo.codigo_monitoreo_pk"), nullable=True)
    codigo_monitoreo_seguimiento_fk = Column(Integer, ForeignKey("tte_monitoreo_seguimiento.codigo_monitoreo_seguimiento_pk"), nullable=True)

    # Fechas
    fecha_registro = Column(DateTime, nullable=True)
    fecha_reporte = Column(DateTime, nullable=True)

    usuario = Column(String(25), nullable=True)

    # Flags / estados
    notificar_reporte = Column(Boolean, nullable=False, default=False)
    enviar_rndc = Column(Boolean, nullable=False, default=False)
    estado_rndc = Column(Boolean, nullable=False, default=False)

    numero_rndc = Column(String(40), nullable=True)
    comentario = Column(String(2000), nullable=True)

    # Relaciones
    monitoreo = relationship(Monitoreo, foreign_keys=[codigo_monitoreo_fk], backref="monitoreos_detalles_monitoreo")
    monitoreo_seguimiento = relationship(MonitoreoSeguimiento, foreign_keys=[codigo_monitoreo_seguimiento_fk], backref="monitoreos_detalles_monitoreo_seguimiento")

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.monitoreo_seguimiento import MonitoreoSeguimiento


class Monitoreo(Base):
    __tablename__ = "tte_monitoreo"

    codigo_monitoreo_pk = Column(Integer, primary_key=True, index=True)

    # Fechas
    fecha_registro = Column(DateTime, nullable=True)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    fecha_ultimo_reporte = Column(DateTime, nullable=True)
    fecha_proximo_reporte = Column(DateTime, nullable=True)

    soporte = Column(String(50), nullable=True)

    # FKs
    codigo_vehiculo_fk = Column(String(20), nullable=True)
    codigo_despacho_fk = Column(Integer, nullable=True)
    codigo_ciudad_destino_fk = Column(String(20), ForeignKey("tte_ciudad.codigo_ciudad_pk"), nullable=True)
    codigo_monitoreo_seguimiento_fk = Column(Integer, ForeignKey("tte_monitoreo_seguimiento.codigo_monitoreo_seguimiento_pk"), nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)

    # Estados
    estado_autorizado = Column(Boolean, nullable=True, default=False)
    estado_aprobado = Column(Boolean, nullable=True, default=False)
    estado_anulado = Column(Boolean, nullable=True, default=False)
    estado_cerrado = Column(Boolean, nullable=True, default=False)
    estado_terminado = Column(Boolean, nullable=True, default=False)

    comentario = Column(String(2000), nullable=True)

    # Relaciones
    ciudad_destino = relationship(Ciudad, foreign_keys=[codigo_ciudad_destino_fk], backref="monitoreos_ciudad_destino")
    monitoreo_seguimiento = relationship(MonitoreoSeguimiento, foreign_keys=[codigo_monitoreo_seguimiento_fk], backref="monitoreos_monitoreo_seguimiento")

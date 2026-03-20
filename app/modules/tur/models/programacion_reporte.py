from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.tur.models.programacion_reporte_tipo import ProgramacionReporteTipo  # noqa: F401


class ProgramacionReporte(Base):
    __tablename__ = "tur_programacion_reporte"

    codigo_programacion_reporte_pk = Column(Integer, primary_key=True, index=True)
    codigo_programacion_fk = Column(Integer, ForeignKey("tur_programacion.codigo_programacion_pk"), index=True)
    codigo_programacion_reporte_tipo_fk = Column(String(10), ForeignKey("tur_programacion_reporte_tipo.codigo_programacion_reporte_tipo_pk"), index=True, nullable=True)
    fecha = Column(DateTime, nullable=True)
    fecha_cierre = Column(DateTime, nullable=True)
    reporta = Column(String(500), nullable=True)
    comentario = Column(String(2000), nullable=True)
    cantidad_respuestas = Column(Integer, default=0)
    estado_autorizado = Column(Boolean, default=False)
    estado_aprobado = Column(Boolean, default=False)
    estado_anulado = Column(Boolean, default=False)
    estado_atendido = Column(Boolean, default=False)
    estado_cerrado = Column(Boolean, default=False)
    dia_desde = Column(Integer, nullable=True)
    dia_hasta = Column(Integer, nullable=True)

    programacion_reporte_tipo = relationship("ProgramacionReporteTipo", foreign_keys=[codigo_programacion_reporte_tipo_fk], primaryjoin="ProgramacionReporte.codigo_programacion_reporte_tipo_fk == ProgramacionReporteTipo.codigo_programacion_reporte_tipo_pk")

    @property
    def programacion_reporte_tipo_nombre(self) -> str | None:
        return self.programacion_reporte_tipo.nombre if self.programacion_reporte_tipo else None

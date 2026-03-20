from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from app.core.tenant_database import Base


class ProgramacionReporteRespuesta(Base):
    __tablename__ = "tur_programacion_reporte_respuesta"

    codigo_programacion_reporte_respuesta_pk = Column("id", Integer, primary_key=True, index=True)
    codigo_programacion_reporte_fk = Column(Integer, ForeignKey("tur_programacion_reporte.codigo_programacion_reporte_pk"), index=True)
    fecha = Column(DateTime, nullable=True)
    respuesta = Column(String(500), nullable=True)

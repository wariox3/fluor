from sqlalchemy import Column, String
from app.core.tenant_database import Base


class ProgramacionReporteTipo(Base):
    __tablename__ = "tur_programacion_reporte_tipo"

    codigo_programacion_reporte_tipo_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(80), nullable=False)

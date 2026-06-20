from sqlalchemy import Column, Integer, String
from app.core.tenant_database import Base


class MonitoreoSeguimiento(Base):
    __tablename__ = "tte_monitoreo_seguimiento"

    codigo_monitoreo_seguimiento_pk = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=True)
    color_fondo = Column(String(15), nullable=True)

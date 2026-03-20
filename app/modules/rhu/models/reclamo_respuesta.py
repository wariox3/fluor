from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from app.core.tenant_database import Base


class ReclamoRespuesta(Base):
    __tablename__ = "rhu_reclamo_respuesta"

    codigo_reclamo_respuesta_pk = Column(Integer, primary_key=True, index=True)
    codigo_reclamo_fk = Column(Integer, ForeignKey("rhu_reclamo.codigo_reclamo_pk"), index=True)
    fecha = Column(DateTime, nullable=True)
    respuesta = Column(String(2000), nullable=True)

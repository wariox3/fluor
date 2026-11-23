from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.tenant_database import Base
from app.core.utils import ahora_local


class LogAccion(Base):
    __tablename__ = "gen_log_accion"
    __table_args__ = (
        Index("idx_modelo_registro", "codigo_modelo_fk", "codigo_registro"),
    )

    codigo_log_accion_pk = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime, nullable=False, default=ahora_local, server_default=func.now())
    codigo_modelo_fk = Column(String(80), ForeignKey("gen_modelo.codigo_modelo_pk"), nullable=False)
    codigo_registro = Column(Integer, nullable=False)
    accion = Column(String(8), nullable=False)  # crear, editar, eliminar
    usuario = Column(String(200), nullable=False)
    ruta = Column(String(50), nullable=True)  # patrón de la ruta HTTP, ej. /tte/guia/{codigo_guia_pk}
    campos = Column(JSON, nullable=True)  # {"campo": valor}

    modelo_rel = relationship("Modelo", back_populates="logs_acciones_modelo_rel")

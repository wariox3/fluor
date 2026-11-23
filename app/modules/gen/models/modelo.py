from sqlalchemy import Boolean, Column, String, false
from sqlalchemy.orm import relationship

from app.core.tenant_database import Base


class Modelo(Base):
    __tablename__ = "gen_modelo"

    codigo_modelo_pk = Column(String(80), primary_key=True)
    codigo_modulo_fk = Column(String(80), nullable=True)
    codigo_funcion_fk = Column(String(30), nullable=True)
    codigo_grupo_fk = Column(String(50), nullable=True)
    descontinuado = Column(Boolean, nullable=True, default=False, server_default=false())
    clase = Column(String(1), nullable=True)  # M=movimiento, D=detalle, C=catalogo, A=administrador, S=soporte

    logs_acciones_modelo_rel = relationship("LogAccion", back_populates="modelo_rel")

from sqlalchemy import Boolean, Column, Integer, String
from app.core.tenant_database import Base


class Cierre(Base):
    __tablename__ = "tte_cierre"

    codigo_cierre_pk = Column(Integer, primary_key=True, index=True)
    anio = Column(Integer, nullable=False, default=0)
    mes = Column(Integer, nullable=False, default=0)
    estado_autorizado = Column(Boolean, nullable=False, default=False)
    estado_aprobado = Column(Boolean, nullable=False, default=False)
    estado_anulado = Column(Boolean, nullable=False, default=False)
    usuario = Column(String(50), nullable=True)
    comentario = Column(String(500), nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)

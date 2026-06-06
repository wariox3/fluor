from sqlalchemy import Boolean, Column, DateTime, Integer, String
from app.core.tenant_database import Base


class Novedad(Base):
    __tablename__ = "tte_novedad"

    codigo_novedad_pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_novedad_tipo_fk = Column(String(20), nullable=True)
    descripcion = Column(String(2000), nullable=True)
    solucion = Column(String(2000), nullable=True)
    fecha = Column(DateTime, nullable=True)
    fecha_registro = Column(DateTime, nullable=True)
    fecha_reporte = Column(DateTime, nullable=True)
    fecha_atencion = Column(DateTime, nullable=True)
    fecha_solucion = Column(DateTime, nullable=True)
    usuario = Column(String(25), nullable=True)
    usuario_solucion = Column(String(25), nullable=True)
    estado_reporte = Column(Boolean, nullable=True, default=False)
    estado_atendido = Column(Boolean, nullable=True, default=False)
    estado_solucion = Column(Boolean, nullable=True, default=False)
    aplica_guia = Column(Boolean, nullable=True, default=False)
    codigo_guia_fk = Column(Integer, nullable=True)
    codigo_despacho_fk = Column(Integer, nullable=True)
    codigo_despacho_referencia_fk = Column(Integer, nullable=True)
    ingreso_api = Column(Boolean, nullable=False, default=False)
    codigo_empresa_fk = Column(Integer, nullable=False)

from sqlalchemy import Boolean, Column, Float, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class Capacitacion(Base):
    __tablename__ = "rhu_capacitacion"

    codigo_capacitacion_pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_capacitacion_tipo_fk = Column(String(10), nullable=True)
    codigo_capacitacion_tema_fk = Column(Integer, nullable=True)
    codigo_puesto_fk = Column(Integer, nullable=True)
    codigo_ciudad_fk = Column(Integer, nullable=True)
    codigo_capacitacion_metodologia_fk = Column(String(10), nullable=True)
    codigo_zona_fk = Column(String(10), nullable=True)
    codigo_subzona_fk = Column(String(10), nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)
    fecha = Column(Date, nullable=True)
    fecha_capacitacion = Column(DateTime, nullable=True)
    usuario = Column(String(80), nullable=True)
    vr_capacitacion = Column(Float, default=0.0)
    contenido = Column(Text, nullable=True)
    objetivo = Column(Text, nullable=True)
    lugar = Column(String(150), nullable=True)
    duracion = Column(String(20), nullable=False)
    facilitador = Column(String(100), nullable=True)
    numero_identificacion_facilitador = Column(String(20), nullable=True)
    numero_personas_asistieron = Column(Integer, nullable=True)
    estado_autorizado = Column(Boolean, default=False, nullable=True)
    estado_aprobado = Column(Boolean, default=False, nullable=True)
    estado_anulado = Column(Boolean, default=False, nullable=True)
    capacitacion_virtual = Column(Boolean, default=False, nullable=True)

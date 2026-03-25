from sqlalchemy import Column, String, Text, Time, Float, Boolean, Integer
from app.core.tenant_database import Base


class Turno(Base):
    __tablename__ = "tur_turno"

    codigo_turno_pk = Column(String(5), primary_key=True, index=True)
    nombre = Column(Text, nullable=True)
    hora_desde = Column(Time, nullable=True)
    hora_hasta = Column(Time, nullable=True)
    horas = Column(Float, default=0.0)
    horas_diurnas = Column(Float, default=0.0)
    horas_nocturnas = Column(Float, default=0.0)
    horas_recargo_nocturno = Column(Float, default=0.0)
    novedad = Column(Boolean, default=False)
    descanso = Column(Boolean, default=False)
    descanso_ordinario = Column(Boolean, default=False)
    incapacidad = Column(Boolean, default=False)
    incapacidad_no_legalizada = Column(Boolean, default=False)
    licencia = Column(Boolean, default=False)
    licencia_no_remunerada = Column(Boolean, default=False)
    vacacion = Column(Boolean, default=False)
    ingreso = Column(Boolean, default=False)
    retiro = Column(Boolean, default=False)
    induccion = Column(Boolean, default=False)
    ausentismo = Column(Boolean, nullable=True, default=False)
    dia = Column(Boolean, nullable=True, default=False)
    noche = Column(Boolean, nullable=True, default=False)
    complementario = Column(Boolean, default=False)
    adicional = Column(Boolean, default=False)
    completo = Column(Boolean, default=False)
    disponible = Column(Boolean, default=False)
    vr_adicional = Column(Float, default=0.0)
    adicional_dia = Column(Boolean, default=False)
    adicional_noche = Column(Boolean, default=False)
    codigo_empresa_fk = Column(Integer)
    estado_inactivo = Column(Boolean, nullable=True, default=False)

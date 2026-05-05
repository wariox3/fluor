from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.tte.models.ruta import Ruta


class Ciudad(Base):
    __tablename__ = "tte_ciudad"

    codigo_ciudad_pk = Column(String(20), primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)

    # División / zona / municipio
    codigo_division = Column(String(10), nullable=True)
    nombre_division = Column(String(100), nullable=True)
    codigo_zona = Column(String(10), nullable=True)
    nombre_zona = Column(String(100), nullable=True)
    codigo_municipio = Column(String(10), nullable=True)
    nombre_municipio = Column(String(100), nullable=True)

    # FKs sin modelo local
    codigo_departamento_fk = Column(String(2), nullable=True)
    codigo_ruta_fk = Column(String(20), ForeignKey("tte_ruta.codigo_ruta_pk"), nullable=True)
    codigo_zona_fk = Column(String(20), nullable=True)
    codigo_cuenta_industria_comercio_fk = Column(String(20), nullable=True)
    codigo_centro_costo_fk = Column(String(20), nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)

    orden_ruta = Column(Integer, nullable=True, default=0)
    codigo_interface = Column(String(10), nullable=True)
    codigo_general = Column(String(10), nullable=True)
    codigo_universal = Column(Integer, nullable=True)

    # Industria y comercio
    porcentaje_industria_comercio = Column(Float, nullable=False, default=0.0)
    vr_base_industria_comercio = Column(Float, nullable=False, default=0.0)

    # Días de despacho
    lunes = Column(Boolean, nullable=True, default=False)
    martes = Column(Boolean, nullable=True, default=False)
    miercoles = Column(Boolean, nullable=True, default=False)
    jueves = Column(Boolean, nullable=True, default=False)
    viernes = Column(Boolean, nullable=True, default=False)
    sabado = Column(Boolean, nullable=True, default=False)
    domingo = Column(Boolean, nullable=True, default=False)

    # Flags
    reexpedicion = Column(Boolean, nullable=True, default=False)
    estado_inactivo = Column(Boolean, nullable=True, default=False)
    ruteo = Column(Boolean, nullable=False, default=False)
    decodificar = Column(Boolean, nullable=False, default=False)

    # Geolocalización (almacenada como texto según entidad origen)
    latitud = Column(String(15), nullable=True)
    longitud = Column(String(15), nullable=True)

    ruta = relationship(Ruta, foreign_keys=[codigo_ruta_fk], backref="ciudades_ruta")

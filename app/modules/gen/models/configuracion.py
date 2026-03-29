from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.gen.models.ciudad import Ciudad


class Configuracion(Base):
    __tablename__ = "gen_configuracion"

    codigo_configuracion_pk = Column(Integer, primary_key=True, index=True)
    nit = Column(String(20))
    digito_verificacion = Column(String(2))
    nombre = Column(String(90))
    telefono = Column(String(25))
    direccion = Column(String(120))
    correo = Column(String(200))
    logo = Column(LargeBinary, nullable=True)
    codigo_empresa_fk = Column(Integer)
    codigo_ciudad_fk = Column(Integer, ForeignKey("gen_ciudad.codigo_ciudad_pk"), nullable=True)
    ruta_almacenamiento_servicio = Column(String(200), nullable=True)

    ciudad_rel = relationship(Ciudad, foreign_keys=[codigo_ciudad_fk])

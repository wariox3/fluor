from sqlalchemy import Column, Integer, String, LargeBinary
from app.core.tenant_database import Base


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

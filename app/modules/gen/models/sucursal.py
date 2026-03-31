from sqlalchemy import Column, Integer, String
from app.core.tenant_database import Base


class Sucursal(Base):
    __tablename__ = "gen_sucursal"

    codigo_sucursal_pk = Column(Integer, primary_key=True, index=True)
    codigo_tercero_fk = Column(Integer, nullable=True)
    nombre = Column(String(50), nullable=True)
    correo_factura_electronica = Column(String(120), nullable=True)
    telefono = Column(String(20), nullable=True)
    contacto = Column(String(150), nullable=True)
    direccion = Column(String(150), nullable=True)
    codigo_ciudad_fk = Column(Integer, nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)

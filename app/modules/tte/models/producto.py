from sqlalchemy import Column, Integer, String
from app.core.tenant_database import Base

class Producto(Base):
    __tablename__ = "tte_producto"

    codigo_producto_pk = Column(String(20), primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)
    codigo_transporte = Column(String(50), nullable=True)
    orden = Column(Integer, nullable=True, default=0)

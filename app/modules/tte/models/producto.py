from sqlalchemy import Column, String
from app.core.tenant_database import Base

class Producto(Base):
    __tablename__ = "tte_producto"

    codigo_producto_pk = Column(String(20), primary_key=True, index=True)            
    nombre = Column(String)

from sqlalchemy import Column, String
from app.core.tenant_database import Base

class Servicio(Base):
    __tablename__ = "tte_servicio"

    codigo_servicio_pk = Column(String(20), primary_key=True, index=True)            
    nombre = Column(String)

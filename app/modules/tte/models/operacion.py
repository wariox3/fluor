from sqlalchemy import Column, String
from app.core.tenant_database import Base

class Operacion(Base):
    __tablename__ = "tte_operacion"

    codigo_operacion_pk = Column(String(20), primary_key=True, index=True)            
    nombre = Column(String)

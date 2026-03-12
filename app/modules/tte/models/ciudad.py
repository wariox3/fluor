from sqlalchemy import Column, String
from app.core.tenant_database import Base

class Ciudad(Base):
    __tablename__ = "tte_ciudad"

    codigo_ciudad_pk = Column(String(20), primary_key=True, index=True)            
    nombre = Column(String)

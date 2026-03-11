from sqlalchemy import Column, Integer, String
from app.core.tenant_database import Base

class Ciudad(Base):
    __tablename__ = "gen_ciudad"

    codigo_ciudad_pk = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)    

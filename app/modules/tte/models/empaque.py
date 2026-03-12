from sqlalchemy import Column, String
from app.core.tenant_database import Base

class Empaque(Base):
    __tablename__ = "tte_empaque"

    codigo_empaque_pk = Column(String(20), primary_key=True, index=True)            
    nombre = Column(String)

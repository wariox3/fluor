from sqlalchemy import (Column, Integer, String)
from sqlalchemy.orm import relationship
from app.core.master_database import Base

class Tenant(Base):
    __tablename__ = "tenant"

    id = Column(Integer, primary_key=True, index=True)    
    nombre = Column(String(100))
    schema = Column(String(100))
    users = relationship("User", back_populates="tenant")
    api_keys = relationship("ApiKey", back_populates="tenant")

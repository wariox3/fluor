
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.master_database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)    
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="users")
    empresa_id = Column(String(100), nullable=False)
    #empresa_id = Column(Integer, ForeignKey("empresa.id"), nullable=False)

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    key_hash = Column(String(255), unique=True, index=True)
    empresa_id = Column(String(100), nullable=False)
    prefix = Column(String(20))
    is_active = Column(Boolean, default=True)
    #created_at = Column(DateTime)  

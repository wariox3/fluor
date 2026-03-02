
from sqlalchemy import (
    Column,
    Integer,
    String
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

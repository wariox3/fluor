from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Numeric, Float
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base

class Programacion(Base):
    __tablename__ = "tur_programacion"

    codigo_programacion_pk = Column(Integer, primary_key=True, index=True)

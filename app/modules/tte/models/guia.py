from sqlalchemy import Column, Integer, String, Date, Numeric
from app.core.tenant_database import Base

class Guia(Base):
    __tablename__ = "tte_guia"

    codigo_guia_pk = Column(Integer, primary_key=True, index=True)

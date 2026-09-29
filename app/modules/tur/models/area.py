from sqlalchemy import Column, String
from app.core.tenant_database import Base


class TurArea(Base):
    __tablename__ = "tur_area"

    codigo_area_pk = Column(String(20), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)

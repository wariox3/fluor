from sqlalchemy import Column, String
from app.core.tenant_database import Base


class Regimen(Base):
    __tablename__ = "gen_regimen"

    codigo_regimen_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(30), nullable=True)
    codigo_interface = Column(String(3), nullable=True)

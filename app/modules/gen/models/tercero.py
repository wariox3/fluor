from sqlalchemy import Column, Integer, String
from app.core.tenant_database import Base

class Tercero(Base):
    __tablename__ = "gen_tercero"

    codigo_tercero_pk = Column(Integer, primary_key=True, index=True)
    nombre_corto = Column(String)
    numero_identificacion = Column(String)

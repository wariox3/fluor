from sqlalchemy import Column, String
from app.core.tenant_database import Base


class Identificacion(Base):
    __tablename__ = "gen_identificacion"

    codigo_identificacion_pk = Column(String(3), primary_key=True, index=True)
    nombre = Column(String(30))

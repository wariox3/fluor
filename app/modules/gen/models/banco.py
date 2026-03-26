from sqlalchemy import Column, String
from app.core.tenant_database import Base


class Banco(Base):
    __tablename__ = "gen_banco"

    codigo_banco_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(30))

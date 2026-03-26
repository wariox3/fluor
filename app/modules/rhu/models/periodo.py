from sqlalchemy import Column, String
from app.core.tenant_database import Base


class Periodo(Base):
    __tablename__ = "rhu_periodo"

    codigo_periodo_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(100))

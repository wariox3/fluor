from sqlalchemy import Column, String
from app.core.tenant_database import Base


class Cargo(Base):
    __tablename__ = "rhu_cargo"

    codigo_cargo_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(200))

from sqlalchemy import Column, String
from app.core.tenant_database import Base


class Grupo(Base):
    __tablename__ = "rhu_grupo"

    codigo_grupo_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(200))

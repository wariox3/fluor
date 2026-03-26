from sqlalchemy import Column, String, LargeBinary
from app.core.tenant_database import Base


class Imagen(Base):
    __tablename__ = "gen_imagen"

    codigo_imagen_pk = Column(String(20), primary_key=True)
    imagen = Column(LargeBinary, nullable=True)
    extension = Column(String(10), nullable=True)

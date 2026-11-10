from sqlalchemy import Column, Float, Integer, String

from app.core.tenant_database import Base


class Arma(Base):
    __tablename__ = "rhu_arma"

    codigo_arma_pk = Column(Integer, primary_key=True, index=True)

    # FKs sin modelo local
    codigo_arma_tipo_fk = Column(String(10), nullable=True)

    nombre = Column(String(200), nullable=True)
    # En milímetros
    calibre = Column(Float, nullable=True)

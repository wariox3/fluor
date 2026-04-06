from sqlalchemy import Column, Integer, Numeric
from app.core.master_database import Base


class Configuracion(Base):
    __tablename__ = "mas_configuracion"

    codigo_configuracion_pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tasa_interes = Column(Numeric(5, 2), nullable=False, default=0)

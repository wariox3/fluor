from sqlalchemy import Boolean, Column, Integer, String, Date, DateTime, Numeric
from app.core.tenant_database import Base

class Guia(Base):
    __tablename__ = "tte_guia"

    codigo_guia_pk = Column(Integer, primary_key=True, index=True)
    codigo_tercero_fk = Column(Integer)
    documento_cliente = Column(String)
    estado_ingreso = Column(Boolean, default=False)
    fecha_ingreso = Column(DateTime)
    estado_despachado = Column(Boolean, default=False)
    fecha_despacho = Column(DateTime)
    estado_entregado = Column(Boolean, default=False)
    fecha_entrega = Column(DateTime)
    estado_cumplido = Column(Boolean, default=False)
    fecha_cumplido = Column(DateTime)
    estado_novedad = Column(Boolean, default=False)
    estado_novedad_solucion = Column(Boolean, default=False)

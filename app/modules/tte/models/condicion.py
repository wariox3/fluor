from sqlalchemy import Boolean, Column, Float, Integer, String
from app.core.tenant_database import Base


class Condicion(Base):
    __tablename__ = "tte_condicion"

    codigo_condicion_pk = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=True)
    codigo_precio_fk = Column(Integer, nullable=True)
    porcentaje_manejo = Column(Float, nullable=False, default=0.0)
    manejo_minimo_unidad = Column(Float, nullable=False, default=0.0)
    manejo_minimo_despacho = Column(Float, nullable=False, default=0.0)
    precio_peso = Column(Boolean, nullable=True, default=False)
    precio_unidad = Column(Boolean, nullable=True, default=False)
    precio_adicional = Column(Boolean, nullable=True, default=False)
    precio_general = Column(Boolean, nullable=True)
    descuento_peso = Column(Float, nullable=False, default=0.0)
    descuento_unidad = Column(Float, nullable=False, default=0.0)
    peso_minimo = Column(Integer, nullable=False, default=0)
    peso_minimo_guia = Column(Integer, nullable=False, default=0)
    limitar_descuento_reexpedicion = Column(Boolean, nullable=True, default=False)
    comentario = Column(String(2000), nullable=True)

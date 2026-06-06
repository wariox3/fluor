from sqlalchemy import Column, Float, Integer, String
from app.core.tenant_database import Base


class CondicionManejo(Base):
    __tablename__ = "tte_condicion_manejo"

    codigo_condicion_manejo_pk = Column(Integer, primary_key=True, index=True)
    codigo_cliente_fk = Column(Integer, nullable=True)
    codigo_tercero_fk = Column(Integer, nullable=True)
    codigo_ciudad_origen_fk = Column(String(20), nullable=True)
    codigo_ciudad_destino_fk = Column(String(20), nullable=True)
    codigo_zona_fk = Column(String(20), nullable=True)
    codigo_cobertura_fk = Column(String(3), nullable=True)
    codigo_pago_fk = Column(String(3), nullable=True)
    porcentaje = Column(Float, nullable=False, default=0.0)
    minimo_unidad = Column(Float, nullable=False, default=0.0)
    minimo_despacho = Column(Float, nullable=False, default=0.0)

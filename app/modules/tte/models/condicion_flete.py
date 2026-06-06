from sqlalchemy import Column, Float, Integer, String
from app.core.tenant_database import Base


class CondicionFlete(Base):
    __tablename__ = "tte_condicion_flete"

    codigo_condicion_flete_pk = Column(Integer, primary_key=True, index=True)
    codigo_cliente_fk = Column(Integer, nullable=True)
    codigo_tercero_fk = Column(Integer, nullable=True)
    codigo_ciudad_origen_fk = Column(String(20), nullable=True)
    codigo_ciudad_destino_fk = Column(String(20), nullable=True)
    codigo_cobertura_fk = Column(String(3), nullable=True)
    codigo_pago_fk = Column(String(3), nullable=True)
    codigo_zona_fk = Column(String(20), nullable=True)
    descuento_peso = Column(Float, nullable=False, default=0.0)
    descuento_unidad = Column(Float, nullable=False, default=0.0)
    peso_minimo = Column(Integer, nullable=False, default=0)
    peso_minimo_guia = Column(Integer, nullable=False, default=0)
    flete_minimo = Column(Float, nullable=False, default=0.0)
    flete_minimo_guia = Column(Float, nullable=False, default=0.0)
    vr_peso = Column(Float, nullable=False, default=0.0)
    vr_unidad = Column(Float, nullable=False, default=0.0)

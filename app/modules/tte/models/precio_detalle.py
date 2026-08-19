from sqlalchemy import Column, Float, ForeignKey, Integer, String
from app.core.tenant_database import Base


class PrecioDetalle(Base):
    __tablename__ = "tte_precio_detalle"

    codigo_precio_detalle_pk = Column(Integer, primary_key=True, index=True)
    codigo_precio_fk = Column(Integer, ForeignKey("tte_precio.codigo_precio_pk"), nullable=True)
    codigo_ciudad_origen_fk = Column(String(20), nullable=True)
    codigo_ciudad_destino_fk = Column(String(20), nullable=True)
    codigo_zona_fk = Column(String(20), ForeignKey("tte_zona.codigo_zona_pk"), nullable=True)
    codigo_producto_fk = Column(String(20), nullable=True)
    codigo_cobertura_fk = Column(String(3), nullable=True)
    vr_peso = Column(Float, nullable=False, default=0.0)
    vr_unidad = Column(Float, nullable=False, default=0.0)
    peso_tope = Column(Float, nullable=False, default=0.0)
    vr_peso_tope = Column(Float, nullable=False, default=0.0)
    vr_peso_tope_adicional = Column(Float, nullable=False, default=0.0)
    minimo = Column(Integer, nullable=False, default=0)

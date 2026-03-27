from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, SmallInteger, Text, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.tenant_database import Base
from sqlalchemy.orm import relationship

class MovimientoDetalle(Base):
    __tablename__ = "gen_movimiento_detalle"

    codigo_movimiento_detalle_pk = Column(Integer, primary_key=True, index=True)
    codigo_movimiento_fk = Column(Integer, nullable=True)
    codigo_item_fk = Column(Integer, nullable=True)
    codigo_tercero_fk = Column(Integer, nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)
    codigo_centro_costo_fk = Column(String(20), nullable=True)
    codigo_impuesto_retencion_fk = Column(String(5), nullable=True)
    codigo_impuesto_industria_comercio_fk = Column(String(5), nullable=True)
    codigo_impuesto_iva_fk = Column(String(5), nullable=True)
    detalle = Column(String(800), nullable=True)
    porcentaje_descuento = Column(Float, nullable=True, default=0.0)
    cantidad = Column(Float, nullable=False, default=0.0)
    cantidad_operada = Column(Float, nullable=False, default=0.0)
    cantidad_pendiente = Column(Float, nullable=False, default=0.0)
    vr_precio = Column(Float, nullable=False, default=0.0)
    operacion_inventario = Column(SmallInteger, nullable=True, default=0)




from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, SmallInteger, Text, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.tenant_database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from app.modules.gen.models.tercero import Tercero

class Movimiento(Base):
    __tablename__ = "gen_movimiento"

    codigo_movimiento_pk = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, nullable=True)
    fecha_vence = Column(Date, nullable=True)
    plazo_pago = Column(Integer, nullable=True, default=0)
    soporte = Column(String(100), nullable=True)
    orden_compra = Column(String(50), nullable=True)
    comentarios = Column(String(500), nullable=True)
    usuario = Column(String(25), nullable=True)    
    operacion_inventario = Column(SmallInteger, nullable=True, default=0)
    operacion_comercial = Column(SmallInteger, nullable=True, default=0)
    codigo_movimiento_tipo_fk = Column(String(10), nullable=False)
    codigo_forma_pago_fk = Column(String(10), nullable=True)
    codigo_asesor_fk = Column(Integer, nullable=True)
    codigo_movimiento_clase_fk = Column(String(10), nullable=False)
    codigo_sucursal_fk = Column(Integer, nullable=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"))
    codigo_centro_costo_fk = Column(String(20), nullable=True)
    codigo_resolucion_fk = Column(Integer, nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)
    codigo_interface = Column(String(20), nullable=True)

    tercero = relationship(Tercero, foreign_keys=[codigo_tercero_fk],backref="movimientos_tercero")
    # Relaciones (ajusta según tus modelos relacionados)
    # codigo_movimiento_tipo = relationship("MovimientoTipo", foreign_keys=[codigo_movimiento_tipo_fk])
    # codigo_forma_pago = relationship("FormaPago", foreign_keys=[codigo_forma_pago_fk])
    # codigo_asesor = relationship("Asesor", foreign_keys=[codigo_asesor_fk])
    # codigo_tercero_destino = relationship("Tercero", foreign_keys=[codigo_tercero_destino_fk])
    # codigo_resolucion = relationship("Resolucion", foreign_keys=[codigo_resolucion_fk])
    # codigo_moneda = relationship("Moneda", foreign_keys=[codigo_moneda_fk])
    

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class Pedido(Base):
    __tablename__ = "tur_pedido"

    codigo_pedido_pk = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, default=0)
    fecha = Column(DateTime, nullable=True)
    codigo_pedido_tipo_fk = Column(String(20))
    codigo_pedido_clase_fk = Column(String(20), nullable=True)
    codigo_pedido_motivo_fk = Column(String(20), nullable=True)
    codigo_clase_fk = Column(Integer, nullable=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    codigo_sector_fk = Column(String(10), nullable=True)
    estado_autorizado = Column(Boolean, default=False)
    estado_aprobado = Column(Boolean, default=False)
    estado_anulado = Column(Boolean, default=False)
    estado_contabilizado = Column(Boolean, default=False)
    estado_programado = Column(Boolean, default=False)
    estado_facturado = Column(Boolean, default=False)
    estado_cerrado = Column(Boolean, default=False)
    horas = Column(Integer, default=0)
    horas_diurnas = Column(Integer, default=0)
    horas_nocturnas = Column(Integer, default=0)
    vr_total_precio_ajustado = Column(Float, default=0)
    vr_total_precio_minimo = Column(Float, default=0)
    vr_subtotal = Column(Float, default=0)
    vr_iva = Column(Float, nullable=True, default=0.0)
    vr_base_iva = Column(Float, default=0.0)
    vr_total = Column(Float, nullable=True, default=0.0)
    usuario = Column(String(50), nullable=True)
    comentario = Column(String(500), nullable=True)
    vr_salario_base = Column(Float, default=0)
    estrato = Column(Integer, nullable=True, default=0)
    codigo_pedido_fk = Column(Integer, nullable=True)
    codigo_empresa_fk = Column(Integer)
    codigo_sucursal_fk = Column(Integer, nullable=True)
    codigo_segmento_fk = Column(String(10), nullable=True)

    tercero_rel = relationship("Tercero", foreign_keys=[codigo_tercero_fk])

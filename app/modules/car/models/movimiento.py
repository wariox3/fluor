from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.gen.models.asesor import Asesor
from app.modules.gen.models.tercero import Tercero
from app.modules.car.models.movimiento_tipo import MovimientoTipo


class Movimiento(Base):
    __tablename__ = "car_movimiento"
    __table_args__ = (
        Index("idx_car_movimiento_fecha_documento", "fecha_documento"),
    )

    codigo_movimiento_pk = Column(Integer, primary_key=True, index=True)
    codigo_movimiento_tipo_fk = Column(String(10), ForeignKey("car_movimiento_tipo.codigo_movimiento_tipo_pk"), nullable=False)
    codigo_movimiento_clase_fk = Column(String(10), nullable=False)
    codigo_cliente_fk = Column(Integer, nullable=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    codigo_cuenta_fk = Column(String(10), nullable=False)
    codigo_asesor_fk = Column(Integer, ForeignKey("gen_asesor.codigo_asesor_pk"), nullable=True)
    codigo_centro_costo_fk = Column(String(20), nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)

    fecha = Column(Date, nullable=False)
    fecha_documento = Column(Date, nullable=True)
    numero = Column(Integer, nullable=False, default=0)
    soporte = Column(String, nullable=True)
    comentarios = Column(Text, nullable=True)
    usuario = Column(String(50), nullable=True)

    vr_total_bruto = Column(Float, nullable=True, default=0.0)
    vr_retencion = Column(Float, nullable=True, default=0.0)
    vr_total_neto = Column(Float, nullable=True, default=0.0)
    vr_consignacion = Column(Float, nullable=True, default=0.0)

    estado_autorizado = Column(Boolean, nullable=True, default=False)
    estado_aprobado = Column(Boolean, nullable=True, default=False)
    estado_anulado = Column(Boolean, nullable=True, default=False)
    estado_contabilizado = Column(Boolean, nullable=True, default=False)

    tercero = relationship(Tercero, foreign_keys=[codigo_tercero_fk], backref="car_movimientos_tercero")
    asesor = relationship(Asesor, foreign_keys=[codigo_asesor_fk], backref="car_movimientos_asesor")
    movimiento_tipo = relationship(MovimientoTipo, foreign_keys=[codigo_movimiento_tipo_fk], backref="movimientos")

    @property
    def tercero_nombre_corto(self):
        return self.tercero.nombre_corto if self.tercero else None

    @property
    def movimiento_tipo_nombre(self):
        return self.movimiento_tipo.nombre if self.movimiento_tipo else None

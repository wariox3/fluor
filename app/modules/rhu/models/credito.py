from sqlalchemy import Boolean, Column, Float, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.models.contrato import Contrato
from app.modules.rhu.models.grupo import Grupo


class Credito(Base):
    __tablename__ = "rhu_credito"

    codigo_credito_pk = Column(Integer, primary_key=True, index=True)
    codigo_credito_tipo_fk = Column(String(10), nullable=True)
    codigo_credito_pago_tipo_fk = Column(String(10), nullable=True)
    codigo_programacion_detalle_fk = Column(Integer, nullable=True)
    codigo_empleado_fk = Column(Integer, ForeignKey("rhu_empleado.codigo_empleado_pk"), nullable=True, index=True)
    codigo_contrato_fk = Column(Integer, ForeignKey("rhu_contrato.codigo_contrato_pk"), nullable=True)
    codigo_grupo_fk = Column(String(10), ForeignKey("rhu_grupo.codigo_grupo_pk"), nullable=True)
    codigo_empresa_fk = Column(Integer)
    fecha = Column(Date)
    fecha_inicio = Column(Date)
    fecha_finalizacion = Column(Date, nullable=True)
    fecha_credito = Column(Date, nullable=True)
    vr_credito = Column(Float, default=0.0)
    vr_cuota = Column(Float, default=0.0)
    vr_cuota_prima = Column(Float, default=0.0)
    porcentaje_descuento = Column(Float, default=0.0)
    vr_abonos = Column(Float, default=0.0)
    vr_saldo = Column(Float, default=0.0)
    numero_cuotas = Column(Integer, default=0, nullable=True)
    numero_cuota_actual = Column(Integer, default=0)
    numero_libranza = Column(String(50), nullable=True)
    comentario = Column(String(200), nullable=True)
    estado_suspendido = Column(Boolean, default=False, nullable=True)
    inactivo_periodo = Column(Boolean, default=False, nullable=True)
    estado_pagado = Column(Boolean, default=False, nullable=True)
    estado_autorizado = Column(Boolean, default=False, nullable=True)
    estado_aprobado = Column(Boolean, default=False, nullable=True)
    estado_anulado = Column(Boolean, default=False, nullable=True)
    usuario = Column(String(50), nullable=True)
    validar_cuotas = Column(Boolean, default=False)
    aplicar_cuota_prima = Column(Boolean, default=False)
    aplicar_cuota_cesantia = Column(Boolean, default=False)

    empleado_rel = relationship("Empleado", foreign_keys=[codigo_empleado_fk])
    contrato_rel = relationship("Contrato", foreign_keys=[codigo_contrato_fk])
    grupo_rel = relationship("Grupo", foreign_keys=[codigo_grupo_fk])

    @property
    def empleado_nombre(self) -> str | None:
        return self.empleado_rel.nombre_corto if self.empleado_rel else None

from sqlalchemy import Boolean, Column, Float, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class Contrato(Base):
    __tablename__ = "rhu_contrato"

    codigo_contrato_pk = Column(Integer, primary_key=True, index=True)
    codigo_empleado_fk = Column(Integer, ForeignKey("rhu_empleado.codigo_empleado_pk"), nullable=True)
    codigo_grupo_fk = Column(String(10), ForeignKey("rhu_grupo.codigo_grupo_pk"), nullable=True)
    codigo_puesto_fk = Column(Integer, ForeignKey("tur_puesto.codigo_puesto_pk"), nullable=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    codigo_cargo_fk = Column(String(10), ForeignKey("rhu_cargo.codigo_cargo_pk"), nullable=True)
    codigo_contrato_tipo_fk = Column(String(10), ForeignKey("rhu_contrato_tipo.codigo_contrato_tipo_pk"), nullable=True)
    fecha_desde = Column(Date)
    fecha_hasta = Column(Date)
    vr_salario = Column(Float)
    estado_terminado = Column(Boolean, default=False)

    empleado_rel = relationship("Empleado", foreign_keys=[codigo_empleado_fk])
    grupo_rel = relationship("Grupo", foreign_keys=[codigo_grupo_fk])
    puesto_rel = relationship("Puesto", foreign_keys=[codigo_puesto_fk])
    tercero_rel = relationship("Tercero", foreign_keys=[codigo_tercero_fk])
    cargo_rel = relationship("Cargo", foreign_keys=[codigo_cargo_fk])
    contrato_tipo_rel = relationship("ContratoTipo", foreign_keys=[codigo_contrato_tipo_fk])

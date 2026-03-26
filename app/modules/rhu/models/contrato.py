from sqlalchemy import Column, Float, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class Contrato(Base):
    __tablename__ = "rhu_contrato"

    codigo_contrato_pk = Column(Integer, primary_key=True, index=True)
    codigo_empleado_fk = Column(Integer, index=True)
    codigo_grupo_fk = Column(String(10), ForeignKey("rhu_grupo.codigo_grupo_pk"), nullable=True)
    codigo_puesto_fk = Column(Integer, ForeignKey("tur_puesto.codigo_puesto_pk"), nullable=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    fecha_desde = Column(Date)
    fecha_hasta = Column(Date)
    vr_salario = Column(Float)

    grupo_rel = relationship("Grupo", foreign_keys=[codigo_grupo_fk])
    puesto_rel = relationship("Puesto", foreign_keys=[codigo_puesto_fk])
    tercero_rel = relationship("Tercero", foreign_keys=[codigo_tercero_fk])

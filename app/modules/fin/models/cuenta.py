from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class FinCuenta(Base):
    __tablename__ = "fin_cuenta"

    codigo_cuenta_pk = Column(String(20), primary_key=True)
    nombre = Column(String(200), nullable=False)
    codigo_cuenta_homologacion_fk = Column(String(20), nullable=True)
    codigo_cuenta_niif_fk = Column(String(20), ForeignKey("fin_cuenta_niif.codigo_cuenta_niif_pk"), nullable=True)
    codigo_clasificacion_fk = Column(String(20), ForeignKey("fin_clasificacion.codigo_clasificacion_pk"), nullable=True)
    codigo_cuenta_padre_fk = Column(String(20), nullable=True)
    permite_movimiento = Column(Boolean, nullable=True, default=False)
    exige_tercero = Column(Boolean, nullable=True, default=False)
    exige_centro_costo = Column(Boolean, nullable=True, default=False)
    exige_base = Column(Boolean, nullable=True, default=False)
    exige_documento_referencia = Column(Boolean, nullable=True, default=False)
    cuenta_pagar = Column(Boolean, nullable=True, default=False)
    porcentaje_base_retencion = Column(Float, nullable=True, default=0.0)
    nivel = Column(Integer, nullable=True, default=1)
    clase = Column(String(1), nullable=True)
    grupo = Column(String(2), nullable=True)
    cuenta = Column(String(4), nullable=True)
    subcuenta = Column(String(6), nullable=True)
    subcuenta_n1 = Column(String(8), nullable=True)
    subcuenta_n2 = Column(String(10), nullable=True)
    codigo_medio_fk = Column(Integer, ForeignKey("fin_medio.codigo_medio_pk"), nullable=True)
    codigo_medio_concepto_fk = Column(Integer, ForeignKey("fin_medio_concepto.codigo_medio_concepto_pk"), nullable=True)
    codigo_medio_valor_fk = Column(String(10), ForeignKey("fin_medio_valor.codigo_medio_valor_pk"), nullable=True)
    codigo_origen_fk = Column(String(30), nullable=True)
    vr_tope = Column(Float, nullable=False, default=0.0)
    codigo_empresa_fk = Column(Integer, ForeignKey("gen_empresa.codigo_empresa_pk"), nullable=False)
    codigo_interface = Column(String(10), nullable=True)

    clasificacion_rel = relationship("FinClasificacion", foreign_keys=[codigo_clasificacion_fk])
    medio_rel = relationship("FinMedio", foreign_keys=[codigo_medio_fk])
    medio_concepto_rel = relationship("FinMedioConcepto", foreign_keys=[codigo_medio_concepto_fk])
    medio_valor_rel = relationship("FinMedioValor", foreign_keys=[codigo_medio_valor_fk])
    empresa_rel = relationship("GenEmpresa", foreign_keys=[codigo_empresa_fk])
    cuenta_niif_rel = relationship("FinCuentaNiif", foreign_keys=[codigo_cuenta_niif_fk])

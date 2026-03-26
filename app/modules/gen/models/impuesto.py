from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.tenant_database import Base
from sqlalchemy.orm import relationship
from app.modules.gen.models.impuesto_tipo import ImpuestoTipo

class Impuesto(Base):
    __tablename__ = "gen_impuesto"

    codigo_impuesto_pk = Column(String(5), primary_key=True, index=True)
    codigo_impuesto_tipo_fk = Column(String(3), ForeignKey("gen_impuesto_tipo.codigo_impuesto_tipo_pk"))
    nombre = Column(String)
    porcentaje = Column(Float, nullable=True, default=0.0)
    base = Column(Float, nullable=True, default=0.0)
    porcentaje_base = Column(Float, nullable=True, default=100)
    clase = Column(String(1), nullable=False, default="G")  # V=Venta, C=Compra, G=General
    codigo_empresa_fk = Column(Integer)    

    impuesto_tipo = relationship(ImpuestoTipo, backref="impuestos_impuesto_tipo")
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from app.core.tenant_database import Base

class Operacion(Base):
    __tablename__ = "tte_operacion"

    codigo_operacion_pk = Column(String(20), primary_key=True, index=True)            
    nombre = Column(String)
    codigo_ciudad_fk = Column(String(20), ForeignKey("tte_ciudad.codigo_ciudad_pk"), nullable=True)
    codigo_operacion_cargo_fk = Column(String(20), ForeignKey("tte_operacion.codigo_operacion_pk"), nullable=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    # FKs sin modelo local (tte_operacion_grupo, fin_centro_costo)
    codigo_operacion_grupo_fk = Column(String(10), nullable=True)
    codigo_centro_costo_fk = Column(String(20), nullable=True)
    cola_rotulo = Column(String(20), nullable=True)
    retencion_industria_comercio = Column(Boolean, nullable=True)

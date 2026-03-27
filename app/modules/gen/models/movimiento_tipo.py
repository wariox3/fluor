from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, SmallInteger, Text, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.tenant_database import Base
from sqlalchemy.orm import relationship

class MovimientoTipo(Base):
    __tablename__ = "gen_movimiento_tipo"

    codigo_movimiento_tipo_pk = Column(String(10), primary_key=True, index=True)
    codigo_movimiento_clase_fk = Column(String(10), nullable=False)
    operacion_inventario = Column(SmallInteger, nullable=True, default=0)
    operacion_comercial = Column(SmallInteger, nullable=True, default=0)

    
